(function(){
	'use strict';
	var feedbackListCntrl = function($state,$stateParams,Feedback,tickets,groups){
		var self =  this;
		this.params = $stateParams;
		this.tickets = tickets.payload.data.data;
		this.total_pages = tickets.payload.data.total_pages;
		this.total_tickets = tickets.payload.data.total_tickets;
		this.groups = groups.payload.data;
		/*
			@paginate object to handle pagination.
		*/
		this.paginate = {
			nextpage : function(){
				self.params.page = self.params.page + 1;
				self.getTickets();
			},
			previouspage : function(){
				self.params.page = self.params.page - 1;
				self.getTickets();
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
		this.getTickets = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};

	};

	angular.module('feedback')
	.controller('feedbackListCntrl', [
		'$state',
		'$stateParams',
		'Feedback',
		'tickets',
		'groups',
		feedbackListCntrl
	]);
})();