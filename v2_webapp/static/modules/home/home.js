(function(){
	'use strict';
	var homeCntrl = function($state,$mdSidenav,$mdDialog,constants,vendorClients){
		// Redirect to admin or vendor page accorfing to the credentials.
		if(vendorClients.$hasRole(constants.userRole.ADMIN)){
			this.admin = true;
			// $state.go('home.opsorder');
		}
		else if(vendorClients.$hasRole(constants.userRole.VENDOR)){
			this.vendor = true;
			// $state.go('home.order');
		}
		// Controller logic for common items between vendor and admin.
		var self = this;
		this.store_name = vendorClients.store_name;
		var confirm = $mdDialog.confirm()
		.parent(angular.element(document.querySelector('#body')))
		.clickOutsideToClose(false)
		.title('Are you sure you want to Sign Out?')
		.textContent('After this you will be redirected to login page.')
		.ariaLabel('Sign Out')
		.targetEvent()
		.ok('Sign Out!')
		.cancel('Not Now')
		.openFrom('#logout-button')
		.closeTo('#logout-button');
		this.toggleSideNav = function(){
			$mdSidenav('left').toggle();
		};
		this.logout = function(){
			vendorClients.$clearUserRole();
			vendorClients.$refresh().then(function (vendor){
				$state.go('login');
			});
		};
		this.showLogoutDialog = function(){
			$mdDialog.show(confirm).then(function(){
				self.logout();
			});
		};
	};

	angular.module('home', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('home',{
			url: "/home",
			templateUrl: "/static/modules/home/home.html",
			controllerAs : 'home',
    		controller: "homeCntrl",
    		resolve: {
    			vendorClients : 'vendorClients',
    			access: ["Access",function (Access){ 
    				return Access.isAuthenticated(); 
    			}]
    		}
		});
	}])
	.controller('homeCntrl', [
		'$state',
		'$mdSidenav',
		'$mdDialog',
		'constants',
		'vendorClients',
		homeCntrl
	]);
})();