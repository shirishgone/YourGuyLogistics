(function(){
	'use strict';
	var LoginCntrl = function ($state,AuthService,$localStorage,vendorClients){
		this.userLogin = function(){
			var data = {
				username : this.username,
				password : this.password
			};
			AuthService.login(data).then(function (response){
				$localStorage.token = response.data.auth_token;
				vendorClients.$refresh().then(function (vendor){
					vendor.$updateuserRole();
					$state.go('home');
				});
			});
		};
	};

	angular.module('login', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('login', {
			url : '/login',
			templateUrl : '/static/modules/login/login.html',
			controllerAs : 'login',
			controller: 'LoginCntrl',
			resolve: {
				vendorClients : "vendorClients",
				access : ["Access",function (Access){
					return Access.isAnonymous();
				}]
			}
		});
	}])
	.controller('LoginCntrl', [
		'$state', 
		'AuthService',
		'$localStorage',
		'vendorClients',
		LoginCntrl
	]);
})();