$(document).ready(function(){
  $('#user_panel').draggable(); // Documents panel
  $('#user_document_list').load("/document/list/");


  var path = location.pathname;
  $.getJSON("/help/get/", { "url":path }, function(json){
     for (var key in json) {
         if (key =='body'){
            qtip_options_.content = json[key];
            $('body').qtip(qtip_options_).show();
	 } else {
	    if (key =='id_page_help'){
	       $('#id_page_help').show();
	       width = 600;
	       tip = false;
	       corner = {
	          target: 'bottomLeft',
		  tooltip: 'topRight'
	       }
	    } else {
		width = 200;
		tip = true;
	        corner = {
	           target: 'topMiddle',
		   tooltip: 'bottomMiddle'
		}
	    }
	    $('#'+key).qtip({
		 content: json[key],
		 show: 'mouseover',
		 hide: 'mouseout',
		 position: {
		    corner: corner
		 },
		 style: { 
		     tip: tip,
		     width: width,
		     background: '#fff',
		     color:'black',
		     name: 'green',
		     border: {
			width: 1,
			radius: 1,
			color: '#606E7B'
		     }
		 }
	     })
          }
      }
  });
});


function follow(object_id, ct, update_object_id, follow){
     $.getJSON('{% url follow_object %}', {"pk":object_id, "ct":ct, 'follow':follow}, function(json){
        var id = '#'+update_object_id;
        $(id).html(json['success']);
     });
}


function voteup(id){
    $.getJSON("/comment/vote/1/", { pk:id }, function(json){
      var cid = "#id_comment_rate-"+id;
      $(cid).text(json['success']);
    });
}

function votedown(id){
    $.getJSON("/comment/vote/-1/", { pk:id }, function(json){
      var cid = "#id_comment_rate-"+id;
      $(cid).text(json['success']);
    });
}

function postvoteup(id){
    $.getJSON("/posts/vote/1/", { pk:id }, function(json){
      var cid = "#id_post_rate-"+id;
      $(cid).text(json['success']);
    });
}

function postvotedown(id){
    $.getJSON("/posts/vote/-1/", { pk:id }, function(json){
      var cid = "#id_post_rate-"+id;
      $(cid).text(json['success']);
    });
}
function delete_document(document_id, element_id){
    $.getJSON("/document/delete/", { document_id:document_id }, function(json){
      $(element_id).text(json['success']);
    });

}



// ---------------------------------------------------------------------------------------



function flag_as_outdated(id,ct){
    $.getJSON("/tags/flag_as_outdated/", { "object_id":id, "content_type":ct }, function(json){
      $("#flag_as_outdated").text(json['success']);
    });
  }

  function readCookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
  }

 function setCookie(c_name,value,expiredays)
    {
       var exdate=new Date();
       exdate.setDate(exdate.getDate()+expiredays);
       document.cookie=c_name+ "=" +escape(value)+
       ((expiredays==null) ? "" : ";expires="+exdate.toUTCString()) + "; path=/";
    }


var spinner = "<img src='/site_media/img/spinner.gif' alt='spinner' />";
function toggle_stick(id){
  var obj = "#"+id;
  if ( $(obj).hasClass('hoverbubble')){
     $(obj).attr('class', 'hoverbubble2');
     $(obj).draggable('option', 'disabled', true);
     $(obj).children().each(function(){
       if ( $(this).hasClass('panel')){
         $(this).html("<img width='20px' src='/site_media/img/pinin.png' />");
       }
     });
     
  } else {
     $(obj).attr('class', 'hoverbubble');
     $(obj).draggable('option', 'disabled', false);
     $(obj).children().each(function(){
       if ( $(this).hasClass('panel')){
         $(this).html("<img width='20px' src='/site_media/img/pinout.png' />");
       }
      });

  }
}

function attachHovers(par) { 
    $(par).find("a.sec, a.psec").each(function() {
        var sec = $(document.createElement("div")).attr('class', 'secbubble');
        $(this).before(sec);
        $(this).remove();
        sec.append(this);
    });

   


    $(par).find("div.secbubble").hover(function() {
        var sticker = false;
        if ($(this).data('active')==1){
            sticker = true;
        }
        $(this).children().each(function(){
            if ( $(this).hasClass('hoverbubble2')==true ){
                sticker = true;
            }
            if ( $(this).hasClass('drag_button')==true ){
                sticker = true;
            }

        });
        if (sticker == false ){
            $(this).data('active', 1);
	    r_id = Math.floor(Math.random()*1000);
	    p_id = r_id+1;
	    var div = $(document.createElement("div")).attr('class', 'hoverbubble').attr('id', r_id).html(spinner);
	    var div_id = "#"+r_id;
	    $(this).append(div);
	    $(div).draggable();

	    var offset = $(this).offset();
	    height = $(this).height();
	    windowoffset = $(document).scrollTop();
	    windowheight = $(window).height();
	    windowbottom = windowoffset + windowheight - 150;
	    if (offset.top > windowbottom) {
	        var newOffset = {
		left: Math.max(0, offset.left - 250),
		top: offset.top - 50
	        };

	    } else {
	        var newOffset = {
		left: Math.max(0, offset.left - 250),
		top: offset.top + 15
	        };
	    }

	    div.offset(newOffset);
	    div.offset(newOffset); // GAH! Chrome/safari bug; we have to do this twice?!
	    // rewrite link for direct access
	    var href = $(this).find("a").attr('href');
	    href = href.replace("#", "");
	    $.get(href, {'context': 'hoverbubble'}, function(data) {
		if (div) {
                    var panel = "<span class='panel' onclick='toggle_stick("+r_id+")'><img width='20px' src='/site_media/img/pinout.png' /></span><br />";
                    rdata = panel + data
		    div.html(rdata);
		    attachHovers(div); 
		    s_id = p_id+1

		    div.draggable()

		}
            });
        }
        
    }, function() {

        var sticker = false;

        $(this).children().each(function(){
            if ( $(this).hasClass('hoverbubble2')==true ){
                sticker = true;
            }
        });
        if (sticker == false){
          $(this).data('active', 2);
          $(this).find(".hoverbubble").fadeOut(function() { $(this).remove(); });
        }
    });
}

function toggle_comments(){
  
  if ($('#comments_block').is(":visible")){
     $('#comments_block').hide('slow');
  } else {
     $('#comments_block').show('slow');
  }
}

function toggle_sections(){
  
  if ($('#sections_block').is(":visible")){
     $('#sections_block').hide('slow');
  } else {
     $('#sections_block').show('slow');
  }
}

$(document).ready(function() {
    $("body").ajaxError(function(evt, xhr, options) {
        if (xhr.status == 404) {
            $(".hoverbubble").html("Section not found.");
        }
    });
    attachHovers("body");

    

});

$(document).ready(function(){

        $('#comments_block').draggable();

        if (location.hash=="#comments"){
          toggle_comments();
        };


	$("#form1").submit(function(){
                if ($("#section_input").val() == '') {
                   alert("Please enter valid section number")
		   return false;
		} else {
                  location.href="/laws/26/"+$("#section_input").val();
                  return false;
                }

	});

	$("#id_tag_form").submit(function(){
                if ($("#id_tag").val() == '') {
                   alert("Please enter tag before submit")
		   return false;
		} else {
                  return true;
                }

	});
});


