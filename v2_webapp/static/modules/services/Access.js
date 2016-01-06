(function(){
	'use strict';
	var Access = function($q,vendorClients){
		var Access = {
			OK: 200,
			UNAUTHORIZED: 401,
    		FORBIDDEN: 403,

    		hasRole : function(role){
    			var deferred = $q.defer();
    			vendorClients.then(function (vendorClients){
    				if(vendorClients.$hasRole(role)){
    					deferred.resolve(Access.OK);
    				}
    				else if(vendorClients.$isAnonymous()){
    					deferred.reject(Access.UNAUTHORIZED);
    				}
    				else{
    					deferred.reject(Access.FORBIDDEN);
    				}
    			});
    			return deferred.promise;
    		},
    		isAuthenticated : function(){
    			var deferred = $q.defer();
    			vendorClients.then(function (vendorClients){
    				if(vendorClients.$isAuthenticated()){
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
    			vendorClients.then(function (vendorClients){
    				if(vendorClients.$isAnonymous()){
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
		'vendorClients',
		Access
	]);
})();