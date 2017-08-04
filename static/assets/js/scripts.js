
jQuery(document).ready(function() {

    /*
        Background slideshow
    */
    // $.backstretch([
    //   "static/assets/img/backgrounds/1.jpg"
    // , "static/assets/img/backgrounds/2.jpg"
    // , "static/assets/img/backgrounds/3.jpg"
    // ], {duration: 3000, fade: 750});

    /*
        Tooltips
    */
    $('.links a.home').tooltip();
    $('.links a.blog').tooltip();

    /*
        Form validation
    */
    $('.register form').submit(function(){
        $(this).find("label[for='name']").html('姓名');
        $(this).find("label[for='mac']").html('MAC地址');
        $(this).find("label[for='class_number']").html('班级');
        $(this).find("label[for='student_id']").html('学号');
        // $(this).find("label[for='password']").html('Password');
        ////
        var firstname = $(this).find('input#name').val();
        var lastname = $(this).find('input#mac').val();
        var username = $(this).find('input#class_number').val();
        var email = $(this).find('input#student_id').val();
        // var password = $(this).find('input#password').val();
        if(firstname == '') {
            $(this).find("label[for='name']").append("<span style='display:none' class='red'> - Please enter your name.</span>");
            $(this).find("label[for='name'] span").fadeIn('medium');
            return false;
        }
        if(lastname == '') {
            $(this).find("label[for='mac']").append("<span style='display:none' class='red'> - Please enter your mac.</span>");
            $(this).find("label[for='mac'] span").fadeIn('medium');
            return false;
        }
        if(username == '') {
            $(this).find("label[for='class_number']").append("<span style='display:none' class='red'> - Please enter a valid class number.</span>");
            $(this).find("label[for='class_number'] span").fadeIn('medium');
            return false;
        }
        if(email == '') {
            $(this).find("label[for='student_id']").append("<span style='display:none' class='red'> - Please enter a valid student id.</span>");
            $(this).find("label[for='student_id'] span").fadeIn('medium');
            return false;
        }
        // if(password == '') {
        //     $(this).find("label[for='password']").append("<span style='display:none' class='red'> - Please enter a valid password.</span>");
        //     $(this).find("label[for='password'] span").fadeIn('medium');
        //     return false;
        // }
    });


});


