(function(){
	'use strict';
	var LoginCntrl = function ($state,AuthService,UserData,$localStorage,vendorClients){
		this.userLogin = function(){
			var data = {
				username : this.username,
				password : this.password
			};
			AuthService.login(data).then(function (response){
				console.log(response.data);
				$localStorage.token = response.data.auth_token;
				vendorClients.$refresh().then(function (response){
					console.log(response);
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
				vendorClients : "vendorClients"
			}
		});
	}])
	.controller('LoginCntrl', [
		'$state', 
		'AuthService',
		'UserData',
		'$localStorage',
		'vendorClients',
		LoginCntrl
	]);
})();