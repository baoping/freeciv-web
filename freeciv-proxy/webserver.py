# -*- coding: latin-1 -*-

''' 
 Freeciv - Copyright (C) 2009 - Andreas R�sdal   andrearo@pvv.ntnu.no
   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2, or (at your option)
   any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
'''

import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import logging
import json
from civcom import *
from debugging import *
from SocketServer import ThreadingMixIn
from urlparse import urlparse

CIVSERVER_ROUNDTRIP_TIME = 0.03;  # 30ms roundtrip time for packets to civserver.

class CivWebServer(ThreadingMixIn, HTTPServer):

  def __init__(self, server_address, RequestHandlerClass):
    self.civcoms = {};
    HTTPServer.__init__(self, server_address, RequestHandlerClass);


  def buffer_send(self, payload_json, key):
    if key in self.civcoms:
      civcom = self.civcoms[key];
      civcom.send_buffer_append(payload_json);

  # get the civcom instance which corresponds to the requested user.
  def get_civcom(self, username, civserverport, civserverhost):
    key = username + str(civserverport) + civserverhost;
    if key not in self.civcoms.keys():
      civcom = CivCom(username, int(civserverport), civserverhost);
      civcom.set_civwebserver(self);
      civcom.start();
      self.civcoms[key] = civcom;
      return civcom;
    else:
      return self.civcoms[key];

class WebserverHandler(BaseHTTPRequestHandler):

    def do_GET(self):
      if (self.path.endswith("status")):
        try:
          self.send_response(200);
          self.send_header('Content-type',    'text/html')
          self.end_headers()
          self.wfile.write(get_debug_info(self.server.civcoms));
        except:
          self.send_error(503, "Service Unavailable.");        
      else:
        self.send_error(500, "Invalid request. HTTP GET not supported.");
      return

    def do_POST(self):        
        url = urlparse(self.path);
        params = dict([part.split('=') for part in url[4].split('&')])
        username = params["u"];
        civserverport = params["p"];
        civserverhost = params["h"];
        
        # check if session is valid.
        if (username == None or civserverport == None or civserverhost == None
            or username == 'null' or civserverport == 'null' or civserverhost == 'null'): 
            self.send_error(500, "Invalid session");
            return;
        
        # get the civcom instance which corresponds to this user.        
        civcom = self.server.get_civcom(username, civserverport, civserverhost);

        try:
          # parse request from webclient
          if self.headers.dict.has_key("content-length"):
            content_length = string.atoi(self.headers.dict["content-length"])
            
            if content_length > 100000:
              self.send_error(503,'Civserver communication failure: size exceeded.')
              return;
            
            post_data = self.rfile.read(content_length)
            
            if self.headers.dict.has_key("content-type"):
                content_type = self.headers.dict["content-type"];
                #logging.error(content_type);
            
            
            # send JSON request to civserver.

            if not civcom.send_packets_to_civserver(post_data):
              logging.info("Sending data to civserver failed.");
              self.send_error(503,'Civserver communication failure: %s' % self.path)
              return;
 
          # Sleep after packets are sent to civserver, to allow 
          # time for packets to arrive at this proxy.
          time.sleep(CIVSERVER_ROUNDTRIP_TIME);

          # prepare reponse to webclient.
                   
          self.send_response(200);
          self.send_header('Content-Type',    'text/html')
          self.end_headers()
          self.wfile.write(civcom.get_send_result_string());
        except Exception, e:
          logging.error(e);
          self.send_error(503, "Service Unavailable. Something is wrong here ");
