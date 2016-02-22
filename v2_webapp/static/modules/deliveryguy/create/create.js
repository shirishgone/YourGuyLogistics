(function(){
	'use strict';
	/*
		dgCreateCntrl is the controller for the delivery guy create page. 
		Its resolved only after loading all the operation manager and team leads.
			
	*/
	var dgCreateCntrl = function ($state,$mdSidenav,dgConstants,DeliveryGuy,leadUserList,PreviousState){
		var self = this;
		/*
			@shift_timings,@transportation_mode : 
			is the list of all the available shift timings and transportation modes for creating dg,
			this is currently static as constant data in constants/constants.js
		*/
		self.shift_timings = dgConstants.shift_timings;
		self.transportation_mode = dgConstants.transportation_mode;
		/*
			@OpsManagers: resolved operation manager list.
			@TeamLeads  : resolved team leads list.
		*/
		self.OpsManagers = leadUserList.OpsManager.payload.data;
		self.TeamLeads   = leadUserList.TeamLead.payload.data;
		/*
			@dg: is a instance of delliveryguy.dg resource for saving the dg data a with ease
		*/
		self.dg = new DeliveryGuy.dg();
		/*
			function to redirect back to the previous page or parent page.
		*/
		self.goBack =function(){
			if(PreviousState.isAvailable()){
				PreviousState.redirectToPrevious();
			}
			else{
				$state.go('home.dgList');
			}
		};
		/*
			create : A function for creation delivery guys and using angular resource.
			It redirects to list view on succesfull creation of dg or handle's error on creation.
		*/
		self.create = function(){
			self.dg.shift_timing = angular.fromJson(self.dg.shift_timing);
			self.dg.$save(function(){
				self.goBack();
			});
		};
	};

	angular.module('deliveryguy')
	.controller('dgCreateCntrl', [
		'$state',
		'$mdSidenav', 
		'dgConstants',
		'DeliveryGuy',
		'leadUserList',
		'PreviousState',
		dgCreateCntrl
	]);
})();