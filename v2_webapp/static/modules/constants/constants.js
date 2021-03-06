(function(){
	'use strict';
	var permissible_tabs = {
		operations : {
			order           : true,
			createOrder     : false,
			assignOrder     : true,
			updateOrder     : true,
			dg              : true,
			dgEdit          : false,
			dgCreate        : false,
			dgPromteTeamLead: false,
			vendor          : true,
			reports         : true,
			COD             : false,
			customer        : false,
			products        : false,
			feedback        : true,
			tutorial        : false,
			notification    : true
		},
		vendor: {
			order           :true,
			createOrder     :true,
			assignOrder     :false,
			updateOrder     :false,
			dg              :false,
			dgEdit          :false,
			dgCreate        :false,
			dgPromteTeamLead:false,
			vendor          :false,
			reports         :true,
			COD             :false,
			customer        :true,
			products        :true,
			feedback        :true,
			tutorial        :true,
			notification    :false
		},
		hr:{
			order           :false,
			createOrder     :false,
			assignOrder     :false,
			updateOrder     :false,
			dg              :true,
			dgEdit          :true,
			dgCreate        :true,
			dgPromteTeamLead:true,
			vendor          :false,
			reports         :false,
			COD             :false,
			customer        :false,
			products        :false,
			feedback        :false,
			tutorial        :false,
			notification    :false
		},
		operations_manager:{
			order           :true,
			createOrder     : false,
			assignOrder     : true,
			updateOrder     : true,
			dg              : true,
			dgEdit          : false,
			dgCreate        : false,
			dgPromteTeamLead: false,
			vendor          : true,
			reports         : true,
			COD             : false,
			customer        : false,
			products        : false,
			feedback        : true,
			tutorial        : false,
			notification    : true
		},
		accounts: {
			order           : false,
			createOrder     : false,
			assignOrder     : false,
			updateOrder     : false,
			dg              : false,
			dgEdit          : false,
			dgCreate        : false,
			dgPromteTeamLead: false,
			vendor          : false,
			reports         : true,
			COD             : true,
			customer        : false,
			products        : false,
			feedback        : false,
			tutorial        : false,
			notification    : false
		},
		sales : {
			order           : true,
			createOrder     : false,
			assignOrder     : false,
			updateOrder     : false,
			dg              : true,
			dgEdit          : false,
			dgCreate        : false,
			dgPromteTeamLead: false,
			vendor          : true,
			reports         : true,
			COD             : false,
			customer        : false,
			products        : false,
			feedback        : true,
			tutorial        : false,
			notification    : false
		},
		sales_manager : {
			order           : true,
			createOrder     : false,
			assignOrder     : false,
			updateOrder     : false,
			dg              : true,
			dgEdit          : false,
			dgCreate        : false,
			dgPromteTeamLead: false,
			vendor          : true,
			reports         : true,
			COD             : false,
			customer        : false,
			products        : false,
			feedback        : true,
			tutorial        : false,
			notification    : true
		},
	};
	var STATUS_OBJECT = [
		{status:'Queued',value:'QUEUED',selected:false},
    	{status:'Intransit',value:'INTRANSIT'},
    	{status:'Out For Delivery',value:'OUTFORDELIVERY'},
    	{status:'Delivered',value:'DELIVERED',selected:false},
    	{status:'Pickup Attempted',value:'PICKUPATTEMPTED',selected:false},
    	{status:'Deliver Attempted',value:'DELIVERYATTEMPTED',selected:false},
    	{status:'Cancelled',value:'CANCELLED',selected:false},
    	{status:'Order Placed',value:'ORDER_PLACED',selected:false},
    	// {status:'Rejected',value:'REJECTED',selected:false},
  	];
  	var dg_checkin_status = [
  		{status:'All',value:'ALL'},
  		{status:'Checked-In',value:'ONLY_CHECKEDIN'},
  		{status:'Not Checked-In',value:'NOT_CHECKEDIN'},
  		{status:'CheckedIn & CheckedOut',value:'CHECKEDIN_AND_CHECKEDOUT'},
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

  	var dg_assignment = [
  		{assignment:'Pickup Unassigned',value:'UNASSIGNED_PICKUP'},
  		{assignment:'Delivery Unassigned',value:'UNASSIGNED_DELIVERY'},
  		{assignment:'Both Unassigned',value:'UNASSIGNED'}
  	];

	var constants = {
		v1baseUrl : '/api/v1/',
		v2baseUrl : '/api/v2/',
		v3baseUrl : '/api/v3/',
		userRole  : { 
			OPS           : 'operations', 
			VENDOR        : 'vendor',
			HR            : 'hr',
			OPS_MANAGER   : 'operations_manager',
			ACCOUNTS      : 'accounts',
			SALES         : 'sales',
			SALES_MANAGER : 'sales_manager'
		},
		status    : STATUS_OBJECT,
		dg_assignment : dg_assignment,
		time      :time_data,
		dg_status : dg_checkin_status,
		permissible_tabs: permissible_tabs,
		ACCESS_KEY : 'AKIAJTRSKA2PKKWFL5PA',
	    SECRET_KEY : 'grJpBB1CcH8ShN6g88acAkDjvklYdgX7OENAx4g/',
	    S3_BUCKET : 'yourguy-pod-test',
	    DEPOSIT_BUCKET: 'bank-deposit-test'
	};
	var prodConstants = {
		v1baseUrl : '/api/v1/',
		v2baseUrl : '/api/v2/',
		v3baseUrl : '/api/v3/',
		userRole  : { 
			OPS           : 'operations', 
			VENDOR        : 'vendor',
			HR            : 'hr',
			OPS_MANAGER   : 'operations_manager',
			ACCOUNTS      : 'accounts',
			SALES         : 'sales',
			SALES_MANAGER : 'sales_manager'
		},
		status    : STATUS_OBJECT,
		dg_assignment : dg_assignment,
		time      : time_data,
		dg_status : dg_checkin_status,
		permissible_tabs : permissible_tabs,
		ACCESS_KEY : 'AKIAJTRSKA2PKKWFL5PA',
	    SECRET_KEY : 'grJpBB1CcH8ShN6g88acAkDjvklYdgX7OENAx4g/',
	    S3_BUCKET : 'yourguy-pod',
	    DEPOSIT_BUCKET: 'bank-deposit'
	};
	var testConstants = {
		v1baseUrl : 'https://yourguytestserver.herokuapp.com/api/v1/',
		v2baseUrl : 'https://yourguytestserver.herokuapp.com/api/v2/',
		v3baseUrl : 'https://yourguytestserver.herokuapp.com/api/v3/',
		userRole  : { 
			OPS           : 'operations', 
			VENDOR        : 'vendor',
			HR            : 'hr',
			OPS_MANAGER   : 'operations_manager',
			ACCOUNTS      : 'accounts',
			SALES         : 'sales',
			SALES_MANAGER : 'sales_manager'
		},
		status    : STATUS_OBJECT,
		dg_assignment : dg_assignment,
		time      : time_data,
		dg_status : dg_checkin_status,
		permissible_tabs: permissible_tabs,
		ACCESS_KEY : 'AKIAJTRSKA2PKKWFL5PA',
	    SECRET_KEY : 'grJpBB1CcH8ShN6g88acAkDjvklYdgX7OENAx4g/',
	    S3_BUCKET  : 'yourguy-pod-test',
	    DEPOSIT_BUCKET: 'bank-deposit-test'
	};

	angular.module('ygVendorApp')
	.constant('constants', prodConstants);
})();