ygVendors.filter('timeFilter', function(){
	return function (input, time){
		if(time == '' || time == undefined ){
			return input;
		}
		var arrayToReturn = []; 
		for(i = 0; i<input.length;i++){
			if(new Date(input[i].last_connected_time) >= new Date(time)){
				arrayToReturn.push(input[i])
			}
		}
		return arrayToReturn;
	}
})

ygVendors.filter('timeAsDate',function ($filter){
	return function (input){
		var time = input.split(':')
		var d = new Date()
	    d.setHours(+time[0]); // set Time accordingly, using implicit type coercion
	    d.setMinutes( time[1]); // you can pass Number or String, it doesn't matter
	    d.setSeconds( time[2]);
	    var x = d.getTimezoneOffset();
	    if(x < 0){
	    	x = Math.abs(x)
	    	d.setMinutes( d.getMinutes() + x); // you can pass Number or String, it doesn't matter
	    }
	    else{
	    	x = Math.abs(x)
	    	d.setMinutes( d.getMinutes()  - x); // you can pass Number or String, it doesn't matter
	    }
	    var _date = $filter('date')(new Date(d), 'hh:mm a');
	    return _date;
	}
})

ygVendors.filter('DgName',function(){
	return function (input){
		var dg_array = []
		dg_array = input
		if(dg_array.length > 0){
			if(dg_array[0].user.username == "UNASSIGNED_PICKUP"){
				dg_array = dg_array.slice(3,dg_array.length)
			}
			return dg_array;
		}
		else{
			return dg_array;
		}
	}
})