(function(){
	'use strict';
	var opsOrderCntrl = function ($state,$mdSidenav,$stateParams,vendorClients,orderResource,orders){
		console.log(orders);
		var self = this;
		this.params = $stateParams;
		this.params.date = new Date(this.params.date);
		this.vendor_list = vendorClients.vendors;
		this.orders = orders.data;
		this.orderFrom = ( ( ( this.params.page -1 ) * 50 ) + 1 );
		this.orderTo  = (this.orderFrom-1) + orders.data.length;
		this.total_pages = orders.total_pages;
		this.total_orders = orders.total_orders;
		this.pending_orders_count = orders.pending_orders_count;
		this.unassigned_orders_count = orders.unassigned_orders_count;


		this.toggleFilter = function(){
			$mdSidenav('order-filter').toggle();
		};

		this.pageRange = function (n){
			return new Array(n);
		};

		this.paginate = {
			nextpage : function(){
				self.params.page = self.params.page + 1;
				self.getOrders();
			},
			previouspage : function(){
				self.params.page = self.params.page - 1;
				self.getOrders();
			}
		};

		this.getOrders = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	var vendorOrderCntrl = function ($state){
		console.log("vendor");
	};

	angular.module('order', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('home.opsorder', {
			url: "^/all-orders?date$vendor&page",
			templateUrl: "/static/modules/order/opsOrders.html",
			controllerAs : 'opsOrder',
    		controller: "opsOrderCntrl",
    		resolve: {
    			vendorClients : 'vendorClients',
    			orderResource : 'Order',
    			access: ["Access","constants", function (Access,constants) { 
    						return Access.hasRole(constants.userRole.ADMIN); 
    					}],
    			orders: ['Order','$stateParams', function (Order,$stateParams){
    						$stateParams.date = ($stateParams.date !== undefined) ? new Date($stateParams.date).toISOString() : new Date().toISOString();
    						$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    						return Order.getOrders.query($stateParams).$promise;
    					}]
    		}
		})
		.state('home.order', {
			url: "^/orders",
			templateUrl: "/static/modules/order/vendorOrders.html",
			controllerAs : 'order',
    		controller: "vendorOrderCntrl",
    		resolve: {
    			vendorClients : 'vendorClients',
    			access: ["Access","constants", function (Access,constants) { 
    				return Access.hasRole(constants.userRole.VENDOR); 
    			}]
    		}
		});
	}])
	.controller('opsOrderCntrl', [
		'$state',
		'$mdSidenav',
		'$stateParams',
		'vendorClients',
		 'orderResource',
		 'orders',
		opsOrderCntrl
	])
	.controller('vendorOrderCntrl', [
		'$state',
		vendorOrderCntrl
	]);
})();