/* Project specific Javascript goes here. */
$('#btnSelectLesson').on('click', function () {
    var language_id = $('#selectlanguage').val();
    var chapter_id = $('#selectchapter').val();
    var book_id = $('#selectbook').val();
    var verse_id = $('#selectverse').val();

    window.location.href = '/record?language=' +
        language_id + '&chapter=' + chapter_id +
        '&book=' + book_id + '&verse=' + verse_id;
});


$('#selectDiv  #selectbook').on('change', function () {

    var book_id = $('#selectbook').val();

    $.ajax({
      type: "POST",
      url: "/getdata/",
      data: {
          "book_id": book_id,
          "csrfmiddlewaretoken": csrf
      },
      cache: false,
      success: function(data){

         var chapter_html = '';
         for (var i=0; i< data["chapters"].length; i++){
             chapter_html += '<option value="' + data["chapters"][i]['id'] + '">' + data["chapters"][i]['title'] + '</option>';
         }
         if (chapter_html != ""){
             $('#selectchapter').html(chapter_html);
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
             $('#selectverse').html(verse_html);
         }
         else {
             alert("There are no verse and lessons to record.");
             return;
         }
      }
    });
});

$('#selectDiv  #selectchapter').on('change', function () {

    var book_id = $('#selectbook').val();

    $.ajax({
      type: "POST",
      url: "/getdata/",
      data: {
          "chapter_id": book_id,
          "csrfmiddlewaretoken": csrf
      },
      cache: false,
      success: function(data){
         var verse_html = '';
         for (var i=0; i< data["verses"].length; i++){
             verse_html += '<option value="' + data["verses"][i]['id'] + '">' + data["verses"][i]['title'] + '</option>';
         }
         if (verse_html != ""){
             $('#selectverse').html(verse_html);
         }
         else {
             alert("There are no verse and lesson to record.");
             return;
         }
      }
    });
});

