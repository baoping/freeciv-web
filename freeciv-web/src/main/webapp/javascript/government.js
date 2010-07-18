/********************************************************************** 
 Freeciv - Copyright (C) 2009 - Andreas Røsdal   andrearo@pvv.ntnu.no
   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2, or (at your option)
   any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
***********************************************************************/

var governments = {};


/**************************************************************************
   ...
**************************************************************************/
function update_govt_dialog()
{
  
  if (client_is_observer()) return;
  
  var governments_list_html = "";
  
  for (var govt_id in governments) {
    var govt = governments[govt_id];
    var bgcolor =  (client.conn.playing['government'] == govt_id) ? "#555555" : "#000000";  
    
    governments_list_html = governments_list_html + "<div style='background-color:" + bgcolor + "' " 
                  + " onclick='send_player_change_government(" + govt['id'] + ");' "
                  + ">" + govt['name'] + "</div>";
  }

  $("#governments_list").html(governments_list_html);


}


/**************************************************************************
 ...
**************************************************************************/
function send_player_change_government(govt_id)
{
  var packet = [{"packet_type" : "player_change_government", 
                "government" : govt_id }];
  send_request (JSON.stringify(packet));
  close_rates_dialog();
}


/**************************************************************************
 Returns the max tax rate for a given government.
 FIXME: This shouldn't be hardcoded, but instead fetched
 from the effects.
**************************************************************************/
function government_max_rate(govt_id)
{ 
  if (govt_id == 0) {
    // Anarchy
    return 100;
  } else if (govt_id == 1) {
    //Despotism
    return 60;
  } else if (govt_id == 2) {
    // Monarchy
    return 70;
  } else if (govt_id == 3) {
    //Communism
    return 80;
  } else if (govt_id == 4) {
    //Republic
    return 80;
  } else if (govt_id == 5) {
    //Democracy
    return 100;
  } else {
    // this should not happen
    return 100;
  }
    
          

}