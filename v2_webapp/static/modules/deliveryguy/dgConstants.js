(function(){
	'use strict';
	/*
		Constant for storing all the static value required for dgs.
		1. Dg shift timings
		2. Dg transportation mode
	*/
	var dgConstantData = {
		shift_timings : [
			{
				start_time : '06:00:00',
				end_time   : '15:00:00'
			},
			{
				start_time : '07:00:00',
				end_time   : '16:00:00'
			},
			{
				start_time : '09:00:00',
				end_time   : '18:00:00'
			},
			{
				start_time : '10:00:00',
				end_time   : '19:00:00'
			},
			{
				start_time : '10:30:00',
				end_time   : '19:30:00'
			},
			{
				start_time : '11:00:00',
				end_time   : '20:00:00'
			},
			{
				start_time : '13:00:00',
				end_time   : '22:00:00'
			},
			{
				start_time : '14:00:00',
				end_time   : '23:00:00'
			}
		],
		transportation_mode : [
			{
				key: 'Biker',
				value : 'BIKER'
			},
			{
				key: 'Walker',
				value : 'WALKER'
			},
			{
				key: 'Car Driver',
				value : 'CAR_DRIVER'
			}
		]
	};

	angular.module('deliveryguy')
	.constant('dgConstants', dgConstantData);
})();