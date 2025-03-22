console.log("Working with javascript functions");

const months = [
    'Jan', 'Feb', 'Mar', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'
];

$("#addReviewForm").submit(function(e) {
    e.preventDefault(); //prevents default behaviour of the form

    let dt = new Date();
    let time = dt.getDay() + ", " + months[dt.getUTCMonth()] + ", " + dt.getFullYear();

    $.ajax({
        data: $(this).serialize(),
        method: $(this).attr("method"),
        url: $(this).attr("action"),
        dataType: "json",
        success: function(response) {
            console.log("Review Saved to database.");

            if(response.bool == true){
                $("#reviewAdded").html("Review Added Successfully!");
                $(".hide-form").hide();
                $(".add-rev-hide").hide();
                $(".hide-p").hide();
                $("#feedbackAdded").html("Thank you for your feedback!");

                let _html = '<div class="review">'
                    _html += '<div class="row no-gutters">'
                    _html += '<div class="col-auto">'
                    // _html += '<a href="#">'+ response.context.user +'</a>'
                    // 
                    _html += '<span class="review-date">' + time + '</span>'
                    _html += '<div class="review-content">'
                    for (let i=0; i<response.context.rating; i++) {
                        _html += '<i class="fas fa-star">'
                        _html += '</i>'
                    }                          
                    _html += '<p>'+ response.context.review
                    _html += '</p>'
                    _html += '</div>'
                    _html += '</div>'

                    $(".reviews").prepend(_html)     
            }
            
        }
    })
})