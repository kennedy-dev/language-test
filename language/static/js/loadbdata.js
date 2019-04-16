/* Project specific Javascript goes here. */
$(document).ready(function () {
    $("#id_book").on('change', function(){
    $.ajax({
          type: "POST",
          url: "/getdata/",
          data: {
              "book_id": $('#id_book').val()
          },
          cache: false,
          success: function (data) {

              var chapter_html = '';
              for (var i = 0; i < data["chapters"].length; i++) {
                  chapter_html += '<option value="' + data["chapters"][i]['id'] + '">' + data["chapters"][i]['title'] + '</option>';
              }
             if (chapter_html != ""){
                $("#id_chapter").html(chapter_html);
             }
             else {
                 alert("There are no chapter and lessons to record.");
                 return;
             }
             var verse_html = '';
             for (var i=0; i< data["verses"].length; i++){
                 verse_html += '<option value="' + data["verses"][i]['id'] + '">' + data["verses"][i]['title'] + '</option>';
             }
             if (verse_html != ""){
                 $('#id_verse').html(verse_html);
             }
             else {
                 alert("There are no verse and lessons to record.");
                 return;
             }

          }});
    });

});


$(document).ready(function () {
    $("#id_chapter").on('change', function(){
    $.ajax({
          type: "POST",
          url: "/getdata/",
          data: {
              "chapter_id": $('#id_chapter').val()
          },
          cache: false,
          success: function (data) {
             var verse_html = '';
             for (var i=0; i< data["verses"].length; i++){
                 verse_html += '<option value="' + data["verses"][i]['id'] + '">' + data["verses"][i]['title'] + '</option>';
             }
             if (verse_html != ""){
                 $('#id_verse').html(verse_html);
             }
             else {
                 alert("There are no verse and lessons to record.");
                 return;
             }
          }});
    });

});

