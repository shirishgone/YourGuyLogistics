(function(){
	'use strict';
	angular.module('ygVendorApp')
	.directive('ydPagination', [function(){
		// Runs during compile
		return {
			// name: '',
			// priority: 1,
			// terminal: true,
			// template: '',
			// templateUrl: '',
			// replace: true,
			// transclude: true,
			// compile: function(tElement, tAttrs, function transclude(function(scope, cloneLinkingFn){ return function linking(scope, elm, attrs){}})),
			// controller: function($scope, $element, $attrs, $transclude) {},
			// require: 'ngModel', // Array = multiple requires, ? = optional, ^ = check parent elements
			/*
				scope {
					@total      : total data count to show as total data.
					@totalPage  : total number of pages the present.
					@params     : all the params that needs to be sent, like page, date etc. it should be a object with madatory page property.
					@listLength : total count of current data list.
					@paginate   : object which contains two function to paginate to next and previous page.
					@pending    : optional! number of pending data which aren't executed yet.
					@unassigned : optional! number of unassigned data which aren't assagined yet.
					@getData    : a function of parent controller to reload the data as params changes. 
				}
			*/
			scope: {
				total       : '@',
				totalPage   : '@',
				params      : '=',
				listLength  : '@',
				paginate    : '=',
				pending     : '@?',
				unassigned  : '@?',
				getData     : '&',
			}, // {} = isolate, true = child, false/undefined = no change
			restrict: 'AE', // E = Element, A = Attribute, C = Class, M = Comment
			link: function($scope, iElm, iAttrs, controller) {
				$scope.orderFrom = ( ( ( $scope.params.page -1 ) * 50 ) + 1 );
				$scope.orderTo  = ($scope.orderFrom-1) + parseInt($scope.listLength);
				$scope.pageRange = function (){
					return new Array(parseInt($scope.totalPage));
				};
			},
			template : [
				'<div class="ydPagination" layout="row" layout-align="start center">',
					'<div class="stats" layout="row">',
						'<p ng-if="pending">Pending: {{pending}} </p>',
						'<p ng-if="unassigned">Unassigned: {{unassigned}} </p>',
						'<p>Total: {{total}} </p>',
					'</div>',
					'<span flex></span>',
					'<div class="pagination" layout="row" layout-align="start center">',
						'<p>Page:</p>',
						'<md-input-container class="md-accent">',
							'<label class="hide-gt-xs">Page</label>',
							'<md-select class="md-accent" ng-model="params.page" ng-change="getData()">',
								'<md-option class="md-accent" ng-repeat="page in pageRange() track by $index" value="{{$index + 1}}">{{$index + 1}}</md-option>',
							'</md-select>',
						'</md-input-container>',
					'</div>',
					'<div class="pagination" layout="row" layout-align="start center">',
						'<p>{{orderFrom}} -- {{orderTo}} of {{total}}</p>',
					'</div>',
					'<div class="page-navigation">',
						'<md-button ng-disabled="params.page == 1" ng-click="paginate.previouspage();" class="md-icon-button md-accent" aria-label="Menu Icon">',
								'<md-icon>arrow_backward</md-icon>',
						'</md-button>',
						'<md-button ng-disabled="params.page == totalPage" ng-click="paginate.nextpage();" class="md-icon-button md-accent" aria-label="Menu Icon">',
								'<md-icon>arrow_forward</md-icon>',
						'</md-button>',
					'</div>',
				'</div>',
			].join('')
		};
	}]);
})();