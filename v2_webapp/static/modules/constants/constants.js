(function(){
	'use strict';
	var STATUS_OBJECT = [
    	{status:'Intransit',value:'INTRANSIT'},
    	{status:'Queued',value:'QUEUED',selected:false},
    	{status:'Delivered',value:'DELIVERED',selected:false},
    	{status:'Order Placed',value:'ORDER_PLACED',selected:false},
    	{status:'Pickup Attempted',value:'PICKUPATTEMPTED',selected:false},
    	{status:'Deliver Attempted',value:'DELIVERYATTEMPTED',selected:false},
    	{status:'Cancelled',value:'CANCELLED',selected:false},
    	{status:'Rejected',value:'REJECTED',selected:false},
  	];
  	var time_data = [
	  	{
	  		value : "00 AM - 06 AM ",
	  		time: {
	  			start_time: 1,
	  			end_time:6
	  		}
	  	},
	  	{
	  		value : "06 AM - 12 PM",
	  		time: {
	  			start_time: 6,
	  			end_time:12
	  		}
	  	},
	  	{
	  		value : "12 PM - 06 PM",
	  		time: {
	  			start_time: 12,
	  			end_time:18
	  		}
	  	},
	  	{
	  		value : "06 PM - 12 AM",
	  		time: {
	  			start_time: 18,
	  			end_time:23
	  		}
	  	}
  	];

	var constants = {
		v1baseUrl: '/api/v1/',
		v2baseUrl: '/api/v2/',
		v3baseUrl: '/api/v3/',
		userRole: {
			ADMIN : 'operations',
			VENDOR : 'vendor'
		},
		status : STATUS_OBJECT,
		time:time_data
	};
	var prodConstants = {
		v1baseUrl: 'http://yourguy.herokuapp.com/api/v1/',
		v2baseUrl: 'http://yourguy.herokuapp.com/api/v2/',
		v3baseUrl: 'http://yourguy.herokuapp.com/api/v3/',
		userRole: {
			ADMIN : 'operations',
			VENDOR : 'vendor'
		},
		status : STATUS_OBJECT,
		time:time_data
	};
	var testConstants = {
		v1baseUrl: 'https://yourguytestserver.herokuapp.com/api/v1/',
		v2baseUrl: 'https://yourguytestserver.herokuapp.com/api/v2/',
		v3baseUrl: 'https://yourguytestserver.herokuapp.com/api/v3/',
		userRole: {
			ADMIN : 'operations',
			VENDOR : 'vendor'
		},
		status : STATUS_OBJECT,
		time:time_data
	};

	angular.module('ygVendorApp')
	.constant('constants', prodConstants);
})();