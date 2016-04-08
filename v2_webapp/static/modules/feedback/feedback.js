(function(){
	'use strict';

	angular.module('feedback', [])
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.feedbackList',{
			url: "^/feedback/list?page",
			templateUrl: "/static/modules/feedback/list/list.html",
			controllerAs : 'feedbackList',
    		controller: "feedbackListCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER,constants.userRole.VENDOR];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    			tickets: ['Feedback','$stateParams', function (Feedback,$stateParams){
    						$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    						return Feedback.getTickets.query($stateParams).$promise;
    					}],
    			groups: ['Feedback', function (Feedback){
    						return Feedback.getGroups.query().$promise;
    					}]
    		}
		})
		.state('home.feedbackDetail',{
			url: "^/feedback/detail/:ticket_id",
			templateUrl: "/static/modules/feedback/detail/detail.html",
			controllerAs : 'feedbackDetail',
    		controller: "feedbackDetailCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER,constants.userRole.VENDOR];
    						return Access.hasAnyRole(allowed_user); 
    					}],
                ticket: ['Feedback','$stateParams', function (Feedback,$stateParams){
                            return Feedback.getTicketsById.get($stateParams).$promise;
                        }],
                groups: ['Feedback', function (Feedback){
                            return Feedback.getGroups.query().$promise;
                        }]
    		}
		});
	}]);
})();