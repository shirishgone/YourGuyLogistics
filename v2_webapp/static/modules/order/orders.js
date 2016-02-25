(function(){
	'use strict';
	var opsOrderCntrl = function ($state,$mdSidenav,$stateParams,DeliveryGuy,orders,constants,orderSelection){
		/*
			 Variable definations
		*/
		var self = this;
		this.params = $stateParams;
		this.statusArray = ($stateParams.dg === undefined) ? [] : $stateParams.dg.split(',');
		this.params.date = new Date(this.params.date);
		/*
			 scope Orders variable assignments are done from this section for the controller
		*/
		this.orders = orders.data;
		this.orderFrom = ( ( ( this.params.page -1 ) * 50 ) + 1 );
		this.orderTo  = (this.orderFrom-1) + orders.data.length;
		this.total_pages = orders.total_pages;
		this.total_orders = orders.total_orders;
		this.pending_orders_count = orders.pending_orders_count;
		this.unassigned_orders_count = orders.unassigned_orders_count;
		/*
			@ status_list: scope order status for eg: 'INTRANSIT' ,'DELIVERED' variable assignments.
			@ time_list: scope order time for time filer variable assignments.
		*/
		this.status_list = constants.status;
		this.time_list = constants.time;
		/*
			@ All method defination for the controller starts from here on.
		*/
		/*
			 @ toggleFilter : main sidenav toggle function, this function toggle the sidebar of the filets of the orders page page.
		*/
		this.toggleFilter = function(){
			$mdSidenav('order-filter').toggle();
		};
		/*
			@pagerange: funxtion for total pages generations for pagination
		*/
		this.pageRange = function (n){
			return new Array(n);
		};
		/*
			@paginate is a function to paginate to the next and previous page of the order list
			@statusSelection is a fucntion to select or unselect the status data in order filter
		*/
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
		this.statusSelection = {
			toggle : function (item , list){
				var idx = list.indexOf(item.value);
        		if (idx > -1) list.splice(idx, 1);
        		else list.push(item.value);
			},
			exists : function (item, list) {
        		return list.indexOf(item.value) > -1;

      		}
		};
		/*
			@dgSearchTextChange is a function for Delivery guy search for filter. When ever the filtered dg change, 
			this function is called.

			@selectedDgChange is a callback function after delivery guy selection in the filter.
		*/
		this.dgSearchTextChange = function(text){
			var search = {
				search : text
			};
			return DeliveryGuy.dgPageQuery.query(search).$promise.then(function (response){
				return response.data;
			});
		};
		this.selectedDgChange = function(dg){
			if(dg){
				self.params.dg = dg.phone_number;
			}
			else{
				self.params.dg = undefined;
			}
			self.getOrders();
		};
		/*
			@getOrders rleoads the order controller according too the filter to get the new filtered data.
		*/
		this.handleOrdeSelection = {
			selectActive : orderSelection.isSelected(),
			numberOfSelectedOrder : orderSelection.slectedItemLength(),
			update : function () {
				self.handleOrdeSelection.selectActive = orderSelection.isSelected();
				self.handleOrdeSelection.numberOfSelectedOrder = orderSelection.slectedItemLength();
			},
			toggle : function(item){
				orderSelection.toggle(item);
				self.handleOrdeSelection.update();
			},
			exists : function(item){
				return orderSelection.exists(item);
			},
			clear : function (){
				orderSelection.clearAll();
				self.handleOrdeSelection.update();
			}
		};
		/*
			@getOrders rleoads the order controller according too the filter to get the new filtered data.
		*/
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
			url: "^/all-orders?date&vendor&dg&status&page",
			templateUrl: "/static/modules/order/opsOrders.html",
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
	.controller('opsOrderCntrl', [
		'$state',
		'$mdSidenav',
		'$stateParams',
		'DeliveryGuy',
		'orders',
		'constants',
		'orderSelection',
		opsOrderCntrl
	])
	.controller('vendorOrderCntrl', [
		'$state',
		vendorOrderCntrl
	]);
})();