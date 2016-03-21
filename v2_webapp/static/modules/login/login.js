(function(){
	'use strict';
	var LoginCntrl = function ($state,AuthService,UserProfile,$localStorage,constants){
		this.loader = false;
		this.userLogin = function(){
			this.loader = true;
			var self = this;
			var data = {
				username : this.username,
				password : this.password
			};
			AuthService.login(data).then(function (response){
				$localStorage.token = response.data.payload.data.auth_token;
				UserProfile.$refresh().then(function (user){
					if(user.role === constants.userRole.OPS_MANAGER || user.role === constants.userRole.OPS){
						$state.go('home.opsorder');
					}
					else if(user.role === constants.userRole.VENDOR){
						$state.go('home.order');
					}
					else if(user.role === constants.userRole.HR){
						$state.go('home.dgList');
					}
					else if(user.role === constants.userRole.ACCOUNTS){
						$state.go('home.cod');
					}
				});
			},function (error){
				self.loader = false;
				self.error_message = error.data.error.message;
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
				UserProfile : "UserProfile",
				access : ["Access",function (Access){
					return Access.isAnonymous();
				}]
			}
		});
	}])
	.controller('LoginCntrl', [
		'$state', 
		'AuthService',
		'UserProfile',
		'$localStorage',
		'constants',
		LoginCntrl
	]);
})();