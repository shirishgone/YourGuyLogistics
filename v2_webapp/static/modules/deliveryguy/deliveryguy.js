(function(){
	'use strict';
	angular.module('deliveryguy', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('home.dgList', {
			url: "^/deliveryguy/list?start_date&end_date&attendance&search&page",
			templateUrl: "/static/modules/deliveryguy/list/list.html",
			controllerAs : 'dgList',
    		controller: "dgListCntrl",
    		resolve : {
    			DeliveryGuy : 'DeliveryGuy',
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER,constants.userRole.HR];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    			dgs: ['DeliveryGuy','$stateParams', function (DeliveryGuy,$stateParams){
    						var x,y;
	    					if(!$stateParams.start_date){
	    						x =  moment();
								x.startOf('day');
	    					}
	    					else{
	    						$stateParams.start_date = moment(new Date($stateParams.start_date));
	    						$stateParams.start_date.startOf('day');
	    					}
	    					if(!$stateParams.end_date){
	    						y =  moment();
								y.endOf('day');
	    					}
	    					else{
	    						$stateParams.end_date = moment(new Date($stateParams.end_date));
	    						$stateParams.end_date.endOf('day');
	    					}
    						$stateParams.start_date = ($stateParams.start_date !== undefined) ? $stateParams.start_date.toISOString() : x.toISOString();
    						$stateParams.end_date = ($stateParams.end_date !== undefined) ?  $stateParams.end_date.toISOString() : y.toISOString();
    						$stateParams.attendance = ($stateParams.attendance!== undefined) ? $stateParams.attendance : 'ALL';
    						$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    						return DeliveryGuy.dgPageQuery.query($stateParams).$promise;
    					}]
    		}
		})
		.state('home.dgCreate', {
			url: "^/deliveryguy/create",
			templateUrl: "/static/modules/deliveryguy/create/create.html",
			controllerAs : 'dgCreate',
    		controller: "dgCreateCntrl",
    		resolve : {
    			DeliveryGuy : 'DeliveryGuy',
    			access: ["Access","constants", function (Access,constants) { 
    						return Access.hasRole(constants.userRole.HR); 
    					}],
    			leadUserList : ['DeliveryGuy','$q', function (DeliveryGuy,$q){
		    				return $q.all ({
		    					TeamLead : DeliveryGuy.dgTeamLeadQuery.query().$promise,
		    					OpsManager : DeliveryGuy.dgOpsManagerQuery.query().$promise
		    				});
    					}],
    		}
		})
		.state('home.dgDetail', {
			url: "^/deliveryguy/detail/:id",
			templateUrl: "/static/modules/deliveryguy/detail/detail.html",
			controllerAs : 'dgDetail',
		 	controller: "dgDetailCntrl",
		 	resolve  : {
		 		DeliveryGuy : 'DeliveryGuy',
		 		access: ["Access","constants", function (Access,constants) { 
		 					var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER,constants.userRole.HR];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    			DG    : ['DeliveryGuy','$stateParams',function(DeliveryGuy,$stateParams){
    						var dg =  new DeliveryGuy.dg();
    						return DeliveryGuy.dg.get($stateParams).$promise;
    					}],
    			leadUserList : ['DeliveryGuy','$q', function (DeliveryGuy,$q){
		    				return $q.all ({
		    					TeamLead : DeliveryGuy.dgTeamLeadQuery.query().$promise,
		    					OpsManager : DeliveryGuy.dgOpsManagerQuery.query().$promise
		    				});
    					}],
		 	}
		});
	}]);
})();