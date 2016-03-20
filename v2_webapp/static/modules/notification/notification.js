(function(){
	'use strict';
    var notificationCntrl = function($scope,$state,$stateParams,$rootScope,Notice,notices){
        var self = this;
        self.params =  $stateParams;
        self.notices = notices.payload.data.data;
        self.total_notifications =  notices.payload.data.total_notifications;
        self.total_pages =  notices.payload.data.total_pages;

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
        $rootScope.$on('notificationUpdated',self.getNotification);

        this.makeAsRead = function(notice){
            Notice.markAsRead.update({id: notice.notification_id},function(response){
            $scope.home.getNoticeCount();
            notice.delivery_id = notice.delivery_id.split(',');
            if(notice.delivery_id.length == 1 && notice.delivery_id.indexOf("") === -1){
                $state.go('home.orderDetail',{id:notice.delivery_id.join()});
            }
            else if(notice.delivery_id.length > 1) {
              $state.go('home.opsorder',{delivery_ids:notice.delivery_id.join()});
            }
            else {
              self.getNotification();
            }
      });
        };
        /*
            @getNotifications rleoads the notification controller according too the filter to get the new filtered data.
        */
        this.getNotifications = function(){
            $state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
        };
    };

	angular.module('notification', [])
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.notification',{
			url: "^/notification?page",
			templateUrl: "/static/modules/notification/notification.html",
			controllerAs : 'notification',
    		controller: "notificationCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    			notices: ['Notice','$stateParams', function (Notice,$stateParams){
    						$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    						return Notice.getNotifications.query($stateParams).$promise;
    					}]
    		}
		});
	}])
    .controller('notificationCntrl', [
        '$scope',
        '$state',
        '$stateParams',
        '$rootScope',
        'Notice',
        'notices',
        notificationCntrl
    ]);
})();