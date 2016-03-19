(function(){
	'use strict';
	var feedbackDetailCntrl = function($state,$stateParams,Feedback,ticket,groups,Notification,PreviousState){
		console.log(ticket);
		var self =  this;
		this.params = $stateParams;
		this.ticket = ticket.payload.data.helpdesk_ticket;
		this.groups = groups.payload.data;
		/*
			function to redirect back to the previous page or parent page.
		*/
		self.goBack = function(){
			if(PreviousState.isAvailable()){
				PreviousState.redirectToPrevious();
			}
			else{
				$state.go('home.feedbackList');
			}
		};
		/*
			@getGroupName function that returns the feedback type based on the group id of the ticket
		*/
		this.getGroupName = function(id){
			if(self.groups){
				for(var i=0 ; i< self.groups.length;i++){
					if(id == self.groups[i].group.id){
						return self.groups[i].group.name;
					}
				}
			}
		};

		/*
			@getTickets rleoads the tickets controller according too the filter to get the new filtered data.
		*/
		this.getTicket = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};

	};

	angular.module('feedback')
	.controller('feedbackDetailCntrl', [
		'$state',
		'$stateParams',
		'Feedback',
		'ticket',
		'groups',
		'Notification',
		'PreviousState',
		feedbackDetailCntrl
	]);
})();