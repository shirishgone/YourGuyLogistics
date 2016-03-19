(function(){
	'use strict';
	var feedbackDetailCntrl = function($state,$stateParams,$mdDialog,Feedback,ticket,groups,Notification,PreviousState,UserProfile,constants){
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
			@getUsername function that returns the name of the user who has updated the note
		*/
		this.getUsername =  function(id){
			if(id == self.ticket.requester_id){
				return self.ticket.requester_name;
			}
			else{
				return self.ticket.responder_name;
			}
		};
		this.showConfirm = function(ev) {
		    // Appending dialog to document.body to cover sidenav in docs app
		    var confirm = $mdDialog.confirm()
		    .title('Are you sure you want to resolve this issue')
		    .ariaLabel('Resolve Feedback')
		    .targetEvent(ev)
		    .ok('Confirm')
		    .cancel('Cancel');
		    $mdDialog.show(confirm).then(function() {
		    	self.closeComplain({});
		    });
		};
		/*
			@addNotes function to add a note for the feedback
		*/
		this.addNotes = function(data){
			Notification.loaderStart();
			data.id = self.ticket.display_id;
			if(UserProfile.$getUserRole() === constants.userRole.VENDOR){
				data.note.helpdesk_note.user_id = self.ticket.requester_id;
			}
			else{
				data.note.helpdesk_note.user_id = self.ticket.responder_id;
			}
			Feedback.addNotes.update(data,function(response){
				self.getTicket();
			});
		};
		/*
			@closeComplain function to close the feedback
		*/
		this.closeComplain = function(data){
			Notification.loaderStart();
			data.id = self.ticket.display_id;
			data.resolve = {
				helpdesk_ticket :{
					status: "5"
				}
			};
			Feedback.resolve.update(data,function(response){
				self.getTicket();
			});
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
		'$mdDialog',
		'Feedback',
		'ticket',
		'groups',
		'Notification',
		'PreviousState',
		'UserProfile',
		'constants',
		feedbackDetailCntrl
	]);
})();