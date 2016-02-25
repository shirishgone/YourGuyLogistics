(function(){
	'use strict';

	var dgDetailCntrl = function($state,$mdDialog,$mdMedia,DeliveryGuy,dgConstants,leadUserList,DG,PreviousState){
		var self = this;
		self.DG = DG.payload.data.data;
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
				templateUrl        : '/static/modules/deliveryguy/dialogs/edit.html',
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
				DeliveryGuy.dg.$update(dg,function(response){
					console.log(response);
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

		self.onlyMonthsPredicate = function(date) {
			var day = moment(date).date();
			return day === 1;
		};

		self.getAttendance = function(){
			var attendance_params = {
				id    : self.DG.id,
				month : moment(self.attendance_date).month() + 1,
   				year  : moment(self.attendance_date).year()
			};
			DeliveryGuy.dg.attendance(attendance_params,function(response){
				self.dg_monthly_attendance = response.payload.data.dg_monthly_attendance[0].attendance;
			});
			// console.log(attendance_params);
		};
	};

	function EditDgCntrl($mdDialog,dgConstants,DG,OpsManagers,TeamLeads){
		var dgEdit = this;
		dgEdit.DG = DG;
		dgEdit.DG.team_lead_ids   = [];
		dgEdit.DG.ops_manager_ids = [];
		dgEdit.DG.team_leads.forEach(function(lead){
			if(lead.dg_id){
				dgEdit.DG.team_lead_ids.push(lead.dg_id);
			}
		});		
		dgEdit.DG.ops_managers.forEach(function(ops){
			dgEdit.DG.ops_manager_ids.push(ops.employee_id);
		});	
		dgEdit.OpsManagers = OpsManagers;
		dgEdit.TeamLeads = TeamLeads;
		console.log(dgEdit.DG);

		dgEdit.shift_timings = dgConstants.shift_timings;
		dgEdit.transportation_mode = dgConstants.transportation_mode;

		dgEdit.cancel = function() {
			$mdDialog.cancel();
		};
		dgEdit.answer = function(answer) {
			$mdDialog.hide(answer);
		};
	}

	angular.module('deliveryguy')
	.controller('dgDetailCntrl', [
		'$state',
		'$mdDialog',
		'$mdMedia',
		'DeliveryGuy',
		'dgConstants',
		'leadUserList',
		'DG',
		'PreviousState',
		dgDetailCntrl
	]);
})();