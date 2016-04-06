(function(){
	'use strict';
	var vendorOrderCntrl = function ($state){
		console.log("vendor");
	};

	angular.module('order', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('home.opsorder', {
			url: "^/all-orders?date&vendor_id&dg_username&order_status&page&start_time&end_time&is_cod&search&delivery_ids&pincodes&is_retail&vendor_name&dg_name",
			templateUrl: "/static/modules/order/list/list.html",
			controllerAs : 'opsOrder',
    		controller: "opsOrderCntrl",
    		resolve: {
    			DeliveryGuy : 'DeliveryGuy',
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    			orders: ['Order','$stateParams', function (Order,$stateParams){
    						$stateParams.date = ($stateParams.date !== undefined) ? new Date($stateParams.date).toISOString() : new Date().toISOString();
    						$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
						    $stateParams.is_cod = ($stateParams.is_cod == 'true')? Boolean($stateParams.is_cod): null;
						    $stateParams.is_retail = ($stateParams.is_retail == 'true')? Boolean($stateParams.is_retail): null;

						    if(Array.isArray($stateParams.order_status)){
    							$stateParams.order_status = ($stateParams.order_status.length > 0) ? $stateParams.order_status.toString(): null;
    						}
    						
    						if(Array.isArray($stateParams.pincodes)){
    							$stateParams.pincodes = ($stateParams.pincodes.length > 0) ? $stateParams.pincodes.toString(): null;
    						}
    						return Order.getOrders.query($stateParams).$promise;
    					}],
    			Pincodes: ['DeliveryGuy',function(DeliveryGuy){
    						return DeliveryGuy.dgServicablePincodes.query().$promise;
    					}]
    		}
		})
        .state('home.orderDetail', {
            url: "^/order/detail/:id",
            templateUrl: "/static/modules/order/detail/detail.html",
            controllerAs : 'orderDetail',
            controller: "orderDetailCntrl",
            resolve: {
                access: ["Access","constants", function (Access,constants) { 
                            var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER,constants.userRole.VENDOR];
                            return Access.hasAnyRole(allowed_user); 
                        }],
                order: ['Order','$stateParams', function (Order,$stateParams){
                            return Order.getOrders.query($stateParams).$promise;
                        }],
            }
        })
		.state('home.order', {
			url: "^/orders",
			templateUrl: "/static/modules/order/vendorOrders.html",
			controllerAs : 'order',
    		controller: "vendorOrderCntrl",
    		resolve: {
    			access: ["Access","constants", function (Access,constants) { 
    				return Access.hasRole(constants.userRole.VENDOR); 
    			}]
    		}
		});
	}])
	.controller('vendorOrderCntrl', [
		'$state',
		vendorOrderCntrl
	]);
})();