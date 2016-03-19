(function(){
	'use strict';
	var Notice = function ($resource,constants){
		return {
			getNotifications : $resource(constants.v3baseUrl+'notification/',{},{
				query :{
					method: 'GET',
				}
			}),
			pendingNotificationCount :$resource(constants.v3baseUrl+'notification/pending/'),
			markAsRead : $resource(constants.v3baseUrl+'notification/:id/read/',{id:'@id'},{
				update :{
					method: 'POST',
				}
			}),
		};
	};
	
	angular.module('ygVendorApp')
	.factory('Notice', [
		'$resource',
		'constants', 
		Notice
	]);
})();