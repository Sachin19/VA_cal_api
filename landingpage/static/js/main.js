$('.range-slider').slider();
$('.value-slider').slider();
$('.check').bootstrapSwitch({'size':'mini'});
$(document).ready(function(){
	timerows = 1;
	locrows = 1;
	// console.log("ok");
	// console.log($('.addingtime').attr("id"));
	$('.addtime').on("click",function(){
		// alert("ok");
		$('.timetable').append("<tr><td><input type=\"text\" class=\"form-control\" name=\"start_time\" placeholder=\"Start time (hh:mm)\"></td><td><input type=\"text\" class=\"form-control\" name=\"end_time\" placeholder=\"End time (hh:mm)\"></td><td><button class=\"btn btn-success removetime\" type=\"button\" id=\"r-"+timerows+"\">Remove</button></td></tr>");
		$('#r-'+timerows).on("click",function(){
			row = $(this).parent().parent();
			// alert(row);
			row.remove();
		});
		timerows+=1;
	});

	$('.addlocation').on("click",function(){
		// alert("ok");
		$('.loctable').append("<tr><td><input type=\"textbox\" class=\"form-control\" name=\"locations\" placeholder=\"\"></td><td><button class=\"btn btn-success removelocation\" id=\"l-"+locrows+"\">Remove</button></td></tr>");
		$('#l-'+locrows).on("click",function(){
			row = $(this).parent().parent();
			// alert(row.html());
			row.remove();
		});
		locrows+=1;
	});
});
