(function(){
	'use strict';

	var dgDetailCntrl = function($state,$stateParams,$mdDialog,$mdMedia,DeliveryGuy,Vendor,dgConstants,leadUserList,DG,PreviousState,Notification){
		var self = this;
		self.params = $stateParams;
		self.DG = DG.payload.data;
		self.attendance_date = moment().date(1).toDate();
		self.attendanceMinDate = moment('2015-01-01').toDate();
		self.attendanceMaxDate = moment().toDate();
		self.OpsManagers = leadUserList.OpsManager.payload.data;
		self.TeamLeads   = leadUserList.TeamLead.payload.data;
		self.showEditDialog = function(){
			var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'));
			$mdDialog.show({
				controller         : ('EditDgCntrl',['$mdDialog','dgConstants','DG','OpsManagers','TeamLeads',EditDgCntrl]),
				controllerAs       : 'dgEdit',
				templateUrl        : '/static/modules/deliveryguy/dialogs/edit.html?nd=' + Date.now(),
				parent             : angular.element(document.body),
				clickOutsideToClose: false,
				fullscreen         : useFullScreen,
				openFrom           : '#dgEditDialog',
				closeTo            : '#dgEditDialog',
				locals             : {
					            DG : self.DG,
					   OpsManagers : self.OpsManagers,
				   		 TeamLeads : self.TeamLeads
				},
			})
			.then(function(dg) {
				Notification.loaderStart();
				dg.shift_time = angular.fromJson(dg.shift_time);
				DeliveryGuy.dg.$update(dg,function(response){
					self.getDgDetails();
					Notification.loaderComplete();
				});
			}, function() {
				self.status = 'You cancelled the dialog.';
			});
		};
		/*
			function to redirect back to the previous page or parent page.
		*/
		self.goBack = function(){
			if(PreviousState.isAvailable()){
				PreviousState.redirectToPrevious();
			}
			else{
				$state.go('home.dgList');
			}
		};
		/*
		*/
		self.deactivateDgDialog = function(){
			var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'));
			$mdDialog.show({
				controller         : ('DeactivateDgCntrl',['$mdDialog','DG',DeactivateDgCntrl]),
				controllerAs       : 'dgDeactivate',
				templateUrl        : '/static/modules/deliveryguy/dialogs/deactivate.html?nd=' + Date.now(),
				parent             : angular.element(document.body),
				clickOutsideToClose: false,
				fullscreen         : useFullScreen,
				locals             : {
					            DG : self.DG
				},
			})
			.then(function(dg) {
				Notification.loaderStart();
				DeliveryGuy.dg.deactivate(dg,function(response){
					Notification.loaderComplete();
					Notification.showSuccess('DG deactivated successfully');
					self.getDgDetails();
				});
			});
		};
		self.onlyMonthsPredicate = function(date) {
			var day = moment(date).date();
			return day === 1;
		};
		self.getTeamMembers = function(){
			DeliveryGuy.dg.associated_dgs({id:self.DG.id},function(response){
				self.associated_dg_list = response.payload.data;
			});
		};
		self.toTeamlead = function(){
			$mdDialog.show({
				controller         : ('AddTeamLeadCntrl',['$mdDialog','DG','DeliveryGuy',AddTeamLeadCntrl]),
				controllerAs       : 'dgTeamLead',
				templateUrl        : '/static/modules/deliveryguy/dialogs/teamlead.html?nd=' + Date.now(),
				parent             : angular.element(document.body),
				clickOutsideToClose: false,
				fullscreen         : true,
				locals             : {
					DG : self.DG,
				},
			})
			.then(function(data) {
				Notification.loaderStart();
				if(self.DG.is_teamlead){
					DeliveryGuy.dg.$update(data,function(response){
						Notification.loaderComplete();
						self.getDgDetails();
					});
				}
				else{
					DeliveryGuy.dg.promoteToTL(data,function(response){
						Notification.loaderComplete();
						self.getDgDetails();
					});
				}
			}, function() {
				self.status = 'You cancelled the dialog.';
			});
		};

		self.associateVendors = function(){
			$mdDialog.show({
				controller         : ('AssociateVendorCntrl',['$mdDialog','DG','Vendor',AssociateVendorCntrl]),
				controllerAs       : 'dgVendors',
				templateUrl        : '/static/modules/deliveryguy/dialogs/associateVendors.html?nd=' + Date.now(),
				parent             : angular.element(document.body),
				clickOutsideToClose: false,
				fullscreen         : true,
				locals             : {
					DG : self.DG,
				},
			})
			.then(function(data) {
				Notification.loaderStart();
				DeliveryGuy.dg.associateVendors(data,function(response){
					Notification.loaderComplete();
					self.getDgDetails();
				});
			});
		};

		self.getAttendance = function(){
			var attendance_params = {
				id    : self.DG.id,
				month : moment(self.attendance_date).month() + 1,
				year  : moment(self.attendance_date).year()
			};
			DeliveryGuy.dg.attendance(attendance_params,function(response){
				self.dg_monthly_attendance = response.payload.data.attendance;
			});
		};

		self.getDgDetails = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	function EditDgCntrl($mdDialog,dgConstants,DG,OpsManagers,TeamLeads){
		var dgEdit = this;
		dgEdit.DG = angular.copy(DG);
		dgEdit.DG.team_lead_dg_ids   = [];
		dgEdit.DG.ops_manager_ids = [];
		dgEdit.DG.team_leads.forEach(function(lead){
			if(lead.dg_id){
				dgEdit.DG.team_lead_dg_ids.push(lead.dg_id);
			}
		});		
		dgEdit.DG.ops_managers.forEach(function(ops){
			dgEdit.DG.ops_manager_ids.push(ops.employee_id);
		});	
		dgEdit.OpsManagers = OpsManagers;
		dgEdit.TeamLeads = TeamLeads;
		dgEdit.shift_timings = dgConstants.shift_timings;
		dgEdit.transportation_mode = dgConstants.transportation_mode;

		dgEdit.findShiftTime = function(shift_time){
			return dgEdit.shift_timings.findIndex(function(shift){
				return shift.start_time == shift_time.start_time;
			});
		};
		dgEdit.DG.shift_time = dgEdit.shift_timings[dgEdit.findShiftTime(dgEdit.DG.shift_time)];

		dgEdit.cancel = function() {
			$mdDialog.cancel();
		};
		dgEdit.answer = function(answer) {
			$mdDialog.hide(answer);
		};
	}

	function AddTeamLeadCntrl($mdDialog,DG,DeliveryGuy){
		var dgTeamLead = this;
		dgTeamLead.DG = DG;
		dgTeamLead.selectedTeamMembers = [];
		dgTeamLead.selectedPincodes = [];
		dgTeamLead.teamLeadData = {
			id: DG.id,
			pincodes : [],
			associate_dgs : []
		};

		dgTeamLead.cancel = function() {
			$mdDialog.cancel();
		};

		DeliveryGuy.dgServicablePincodes.query().$promise.then(function (response){
				dgTeamLead.pincodes =  response.payload.data;
		});

		dgTeamLead.addTeamDgs = function(chip){
			dgTeamLead.teamLeadData.associate_dgs.push(chip.id);
		};
		dgTeamLead.removeTeamDgs = function(chip){
			var index = dgTeamLead.teamLeadData.associate_dgs.indexOf(chip.id);
			dgTeamLead.teamLeadData.associate_dgs.splice(index,1);
		};
		dgTeamLead.addTlPincode = function(chip){
			dgTeamLead.teamLeadData.pincodes.push(chip.pincode);
		};
		dgTeamLead.removeTlPincode = function(chip){
			var index = dgTeamLead.teamLeadData.pincodes.indexOf(chip.pincode);
			dgTeamLead.teamLeadData.pincodes.splice(index,1);
		};

		dgTeamLead.dgSearch = function(text){
			var search = {
				search : text
			};
			return DeliveryGuy.dgPageQuery.query(search).$promise.then(function (response){
				return response.payload.data.data;
			});
		};

		dgTeamLead.transformChip = function(chip) {
			// If it is an object, it's already a known chip
			if (angular.isObject(chip)) {
				return {name: chip.name, phone_number: chip.phone_number,id: chip.id};
			}
		};

		dgTeamLead.transformPinChip = function(chip) {
			// If it is an object, it's already a known chip
			if (angular.isObject(chip)) {
				return chip;
			}
		};

		dgTeamLead.submitTlData = function(){
			$mdDialog.hide(dgTeamLead.teamLeadData);
		};
	}

	function DeactivateDgCntrl($mdDialog,DG){
		var dgDeactivate = this;
		dgDeactivate.DG = DG;

		dgDeactivate.cancel = function() {
			$mdDialog.cancel();
		};

		dgDeactivate.answer = function(answer){
			answer.id = dgDeactivate.DG.id;
			$mdDialog.hide(answer);
		};
	}

	function AssociateVendorCntrl($mdDialog,DG,Vendor){
		var dgVendors = this;
		dgVendors.DG = angular.copy(DG);
		dgVendors.selectedVendors = dgVendors.DG.associated_vendors;

		dgVendors.vendorSearch = function(text){
			var search = {
				search : text
			};
			return Vendor.query(search).$promise.then(function (response){
				return response.payload.data.data;
			});
		};

		dgVendors.transformVendorChip = function(chip) {
			// If it is an object, it's already a known chip
			if (angular.isObject(chip)) {
				return chip;
			}
		};

		dgVendors.cancel = function(){
			$mdDialog.cancel();
		};

		dgVendors.answer = function(answer){
			var vendorData  = {
				vendor_ids : []
			};
			answer.forEach(function(vend){
				vendorData.vendor_ids.push(vend.id);
			});
			vendorData.id = dgVendors.DG.id;
			$mdDialog.hide(vendorData);
		};
	}

	angular.module('deliveryguy')
	.controller('dgDetailCntrl', [
		'$state',
		'$stateParams',
		'$mdDialog',
		'$mdMedia',
		'DeliveryGuy',
		'Vendor',
		'dgConstants',
		'leadUserList',
		'DG',
		'PreviousState',
		'Notification',
		dgDetailCntrl
	]);
})();