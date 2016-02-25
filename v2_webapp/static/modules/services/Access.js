(function(){
	'use strict';
	var Access = function($q,UserProfile){
		var Access = {
			OK: 200,
			UNAUTHORIZED: 401,
    		FORBIDDEN: 403,

    		hasRole : function(role){
    			var deferred = $q.defer();
    			UserProfile.then(function (UserProfile){
    				if(UserProfile.$hasRole(role)){
    					deferred.resolve(Access.OK);
    				}
    				else if(UserProfile.$isAnonymous()){
    					deferred.reject(Access.UNAUTHORIZED);
    				}
    				else{
    					deferred.reject(Access.FORBIDDEN);
    				}
    			});
    			return deferred.promise;
    		},
            hasAnyRole: function(roles) {
                var deferred = $q.defer();
                UserProfile.then(function(userProfile) {
                    if (userProfile.$hasAnyRole(roles)) {
                        deferred.resolve(Access.OK);
                    } else if (userProfile.$isAnonymous()) {
                        deferred.reject(Access.UNAUTHORIZED);
                    } else {
                        deferred.reject(Access.FORBIDDEN);
                    }
                });
              return deferred.promise;
            },
    		isAuthenticated : function(){
    			var deferred = $q.defer();
    			UserProfile.then(function (UserProfile){
    				if(UserProfile.$isAuthenticated()){
    					deferred.resolve(Access.Ok);
    				}
    				else{
    					deferred.reject(Access.UNAUTHORIZED);
    				}
    			});
    			return deferred.promise;
    		},
    		isAnonymous : function(){
    			var deferred = $q.defer();
    			UserProfile.then(function (UserProfile){
    				if(UserProfile.$isAnonymous()){
    					deferred.resolve(Access.OK);
    				}
    				else{
    					deferred.reject(Access.FORBIDDEN);
    				}
    			});
    			return deferred.promise;
    		}
		};
        return Access;
	};

	angular.module('ygVendorApp').
	factory('Access', [
		'$q',
		'UserProfile',
		Access
	]);
})();