(function(){
	'use strict';
	var DeliverGuy = function ($resource,constants){
		return {
			dg : $resource(constants.v3baseUrl+'deliveryguy/:id/',{id:"@id"},{
				query :{
					method: 'GET',
					isArray: true
				},
				$update : {
					url : constants.v3baseUrl+'deliveryguy/:id'+'/edit_dg_details/',
					method: 'PUT'
				},
				attendance : {
					url : constants.v3baseUrl+'deliveryguy/:id'+'/attendance/',
					method : 'PUT'
				}
			}),
			dgPageQuery : $resource(constants.v3baseUrl+'deliveryguy/:id/',{id:"@id"},{
				query :{
					method: 'GET',
					isArray: false
				}
			}),
			dgTeamLeadQuery : $resource(constants.v3baseUrl+'deliveryguy/teamleads/', {}, {
				query : {
					method : 'GET',
					isArray : false
				}
			}),
			dgOpsManagerQuery : $resource(constants.v3baseUrl+'deliveryguy/ops_executives/', {}, {
				query : {
					method : 'GET',
					isArray : false
				}
			}),
		};
	};
	
	angular.module('ygVendorApp')
	.factory('DeliveryGuy', [
		'$resource',
		'constants', 
		DeliverGuy
	]);
})();