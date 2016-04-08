(function(){
	'use strict';
	var codCntrl = function($state,$stateParams,$mdSidenav){
		if($state.current.name == 'home.cod.deposit'){
			this.selectedIndex = 0;
		}
		else if($state.current.name == 'home.cod.transfer'){
			this.selectedIndex = 1;
		}
		else if($state.current.name == 'home.cod.history'){
			this.selectedIndex = 2;
		}
		else {
			this.selectedIndex = 0;
		}
		/*
			 @ toggleFilter : main sidenav toggle function, this function toggle the sidebar of the filets of the orders page page.
		*/
		this.toggleFilter = function(){
			$mdSidenav('cod-filter').toggle();
		};
		
	};

	angular.module('Cod', [])
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.cod',{
			url: "^/cod",
			templateUrl: "/static/modules/cod/cod.html",
			controllerAs : 'cod',
    		controller: "codCntrl",
   			redirectTo: 'home.cod.deposit',
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.ACCOUNTS];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    		}
		});
	}])
	.controller('codCntrl', [
		'$state',
		'$stateParams',
		'$mdSidenav',
		codCntrl
	]);
})();