(function(){
	'use strict';
	var Feedback = function($resource,constants){
		return {
			getGroups : $resource(constants.v3baseUrl+'freshdesk/groups/',{}, {
				query : {
					method : 'GET',
					cache : true
				}
			}),
			getTicketsById : $resource(constants.v3baseUrl+'freshdesk/get_ticket/'),
			getTickets : $resource(constants.v3baseUrl+'freshdesk/all_tickets/',{},{
				query :{
					method: 'GET',
				}
			}),
			addNotes : $resource(constants.v3baseUrl+'freshdesk/add_note/',{},{
				update :{
					method: 'POST',
				}
			}),
			resolve : $resource(constants.v3baseUrl+'freshdesk/resolve/',{},{
				update :{
					method: 'PUT',
				}
			}),
		};
	};
	angular.module('ygVendorApp')
	.factory('Feedback', [
		'$resource',
		'constants',
		Feedback
	]);

})();