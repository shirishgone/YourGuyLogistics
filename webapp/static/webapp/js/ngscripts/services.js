ygVendors.factory('Errorhandler', function(){
    var handler = {};
    var respObject = {};

    handler.successStatus = function(response){
        // console.log(response)
        if(response.status === 200 || response.status === 201){
            respObject.has_error = false;
            respObject.error = null;
            respObject.data = response.data;
        }
    };

    handler.errorStatus = function(response){
        if(response.status >= 400 && response.status < 500){
            if(response.status == 404){
                respObject.has_error = true;
                respObject.error = response.data.detail;
                respObject.data = null;
                return;
            }
            respObject.has_error = true;
            if(response.data.error){
                respObject.error = response.data.error;
            }
            else if(response.data.description){
                respObject.error = response.data.description;
            }
            respObject.data = null;
        }
        else if(response.status >= 500 && response.status < 600){
            respObject.has_error = true;
            respObject.error = "Something went wrong";
            respObject.data= null;
        }
    };

    handler.getStatus = function(){
        return respObject;
    };

    handler.clear = function(){
        respObject.has_error = false;
        respObject.error = null;
        respObject.data = null;
    };

    return handler;
});

ygVendors.factory('AuthService', function ($http,$rootScope,StoreSession,baseURl,Errorhandler){
	var authService = {};

	authService.login = function(data,success,error){
      var request = {
        url: baseURl.apiURL+'/auth/login/',
        method:'POST',
        data: data
      };
      $http(request).success(success).error(error);
    };

    authService.signup = function(data){
    	var request = {
    		url: baseURl.V2apiURL+'/vendor/0/request_vendor_account/',
    		method:'POST',
    		data:data
    	};
    	return $http(request).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    return authService;
});

ygVendors.service('StoreSession', function ($localStorage){
	this.create = function(token,username){
		$localStorage.token = token;
		$localStorage.username = username;
	};

    this.getUsername = function(){
        return $localStorage.username;
    };

	this.destroy = function(){
		delete $localStorage.token;
		delete $localStorage.username;
        delete $localStorage.customers;
	};

    this.addCustomer = function(data){
        delete $localStorage.customers;
        $localStorage.customers = data;
    };

    this.getCustomer = function(){
        return $localStorage.customers;
    };

    this.pushCustomer = function(data){
        $localStorage.customers.unshift(data);
    };

    this.removeCustomer = function(data){
        for(i = $localStorage.customers.length-1; i>=0; i--) {
            if( $localStorage.customers[i].id == data.id ){
                 $localStorage.customers.splice(i,1);
            }
        }
    };

    this.updateCustomer = function(data){
        for(i = $localStorage.customers.length-1; i>=0; i--) {
            if( $localStorage.customers[i].id == data.id ){
                 $localStorage.customers[i] = data;
            }
        }
    };
});

ygVendors.factory('Orders',function ($http,baseURl,$q,Errorhandler){
	var getOrders = {};
    
	getOrders.fetchOrder = function(success,error){
		$http.get(baseURl.apiURL+"/order/").success(success).error(error);
	};

    getOrders.fetchOrderForDate = function(data){
        if(data.vendor){
            vendor_string = "&vendor_id="+data.vendor;
        }
        else{
            vendor_string = "";
        }
        if(data.dg){
            dg_string = "&dg_username="+data.dg;
        }
        else{
            dg_string = "";
        }
        if(data.status){
            status_string = "&order_status="+data.status;
        }
        else{
            status_string = "";
        }
        if(data.page){
            page_string = "&page="+data.page;
        }
        else{
            page_string = "";
        }
        if(data.search){
            order_id_string = "&search="+data.search;
        }
        else{
            order_id_string = "";
        }
        start_time_string = (data.start_time)? "&time_start="+data.start_time:"";
        end_time_string = (data.end_time)? "&time_end="+data.end_time:"";
        cod_string = (data.cod)? "&is_cod="+data.cod:"";


        return $http.get(baseURl.V2apiURL+"/order/?date="+data.date+vendor_string+dg_string+status_string+page_string+order_id_string+cod_string+start_time_string+end_time_string).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    getOrders.createOrder = function (data){
        Errorhandler.clear();
        return $http.post(baseURl.V2apiURL+"/order/",data).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    getOrders.getOrderById = function(data){
        Errorhandler.clear();
        return $http.get(baseURl.V2apiURL+"/order/"+data.orderId+"/?date="+data.dateId).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    getOrders.deleteOrder = function(id){
        Errorhandler.clear();
        return $http.post(baseURl.V2apiURL+"/order/"+id+"/cancel/").then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    getOrders.approveOrder = function(data){
        var json = {date:data.date,rejection_reason:data.message};
        return $http.post(baseURl.apiURL+'/order/'+data.id+'/'+data.status+'/',json).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    getOrders.rescheduleOrder = function(id,data){
        Errorhandler.clear();
        return $http.post(baseURl.apiURL+'/order/'+id+'/reschedule/',data).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    getOrders.fileUpload = function(data){
        Errorhandler.clear();
        return $http.post(baseURl.V2apiURL+"/order/0/upload_excel/",data).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    getOrders.updateIntransitStatus = function(orders_to_update){
        var req_array = [];
        for(var i=0; i< orders_to_update.length;i++){
            req_array.push($http.post(baseURl.V2apiURL+"/order/"+orders_to_update[i].id+"/picked_up/",orders_to_update[i]));
        }
        var deferred =  $q.defer();
        $q.all(req_array).then(function (value){
            deferred.resolve("success");
        }, function (error){
            deferred.reject("One or more status not updated\n"+error.data.error);
        });
        return deferred.promise;
    };

    getOrders.updateDeliveredStatus = function(orders_to_update){
        var req_array = [];
        for(var i=0; i< orders_to_update.length;i++){
            req_array.push($http.post(baseURl.V2apiURL+"/order/"+orders_to_update[i].id+"/delivered/",orders_to_update[i]));
        }
        var deferred =  $q.defer();
        $q.all(req_array).then(function (value){
            deferred.resolve("success");
        }, function (error){
            deferred.reject("One or more status not updated\n"+error.data.error);
        });
        return deferred.promise;
    };

    getOrders.assignOrder = function(orders_to_assign){
        var req_array = [];
        for(var i=0;i < orders_to_assign.length;i++){
            req_array.push($http.post(baseURl.V2apiURL+"/order/0/assign_order/",orders_to_assign[i]));
        }
        var deferred =  $q.defer();
        $q.all(req_array).then(function (data){
            deferred.resolve("success");
        }, function (error){
            deferred.reject(error.data.error);
        });
        return deferred.promise;
    };

    getOrders.searchCustomer = function(query){
        Errorhandler.clear();
        return $http.get(baseURl.V2apiURL+'/consumer/?search='+query).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

	return getOrders;
});

ygVendors.factory('Consumers',function ($http,Errorhandler,baseURl){
    var consumers = {};
    consumers.fetchConsumer = function(data){
        Errorhandler.clear();
        if(data.search){
            search_string = "&search="+data.search;
        }
        else {
            search_string = "";
        }
        return $http.get(baseURl.V2apiURL+"/consumer/?page="+data.page+search_string).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    consumers.fetchConsumerv1 = function(){
        Errorhandler.clear();
        return $http.get(baseURl.apiURL+"/consumer/").then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    consumers.create = function(data){
        Errorhandler.clear();
        return $http.post(baseURl.V2apiURL+"/consumer/",data).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    consumers.deleteConsumer = function(id){
        Errorhandler.clear();
        return $http.delete(baseURl.apiURL+'/consumer/'+id+'/').then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    consumers.getConsumerById = function(id){
        Errorhandler.clear();
        return $http.get(baseURl.V2apiURL+'/consumer/'+id+'/').then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    consumers.addAddress = function(id,data){
        Errorhandler.clear();
        return $http.post(baseURl.V2apiURL+'/consumer/'+id+'/add_address/',data).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    consumers.deleteAddress = function(id,data){
        Errorhandler.clear();
        return $http.post(baseURl.apiURL+'/consumer/'+id+'/remove_address/',data).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    return consumers;
});

ygVendors.factory('Products', function ($http,Errorhandler,baseURl){
    var product = {};
    product.getProduct = function(){
        Errorhandler.clear();
        return $http.get(baseURl.V2apiURL+"/product/").then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    product.getCategory = function(){
        Errorhandler.clear();
        return $http.get(baseURl.apiURL+"/productcategory/").then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    product.createProduct = function(data){
        Errorhandler.clear();
        return $http.post(baseURl.apiURL+"/product/",data).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    return product;
});

ygVendors.factory('Codes', function ($http,baseURl,Errorhandler){
    var codes = {};
    codes.getAreCode = function(){
        return $http.get(baseURl.apiURL+"/area/");
    };

    codes.getProductCodes = function(){
        return $http.get(baseURl.apiURL+"/product/").then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };
    return codes;
});

ygVendors.factory('Vendors',function ($http,baseURl,Errorhandler){
    var Vendors = {};
    Vendors.getVendor = function(){
        return $http.get(baseURl.V2apiURL+'/vendor/');
    };

    Vendors.getRequestedVendor = function(){
        return $http.get(baseURl.V2apiURL+'/vendor/requestedvendors/').then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    Vendors.getVendorById = function(id){
        return $http.get(baseURl.V2apiURL+'/vendor/'+id+'/').then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    Vendors.approveById = function(id,notes){
        return $http.post(baseURl.apiURL+'/vendor/'+id+'/approve/',notes).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };
    Vendors.addAddress = function(id,data){
        Errorhandler.clear();
        return $http.post(baseURl.V2apiURL+'/vendor/'+id+'/add_address/',data).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    Vendors.deleteAddress = function(id,data){
        Errorhandler.clear();
        return $http.post(baseURl.apiURL+'/vendor/'+id+'/remove_address/',data).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };
    
    return Vendors;
});

ygVendors.factory('DG',function ($http,baseURl,Errorhandler){
    var Dg = {};
    Dg.getDgv2 = function(data){
        var search_string;
        if(data.search){
            search_string = "&search="+data.search;
        }
        else{
            search_string = '';
        }
        return $http.get(baseURl.V2apiURL+'/delivery_guy/?date='+data.date+'&page='+data.page+'&attendance_status='+data.attendance+search_string).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    Dg.getDgv1 = function(){
        return $http.get(baseURl.apiURL+'/deliveryguy/').then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    Dg.createDg = function (data){
        return $http.post(baseURl.apiURL+'/register/',data).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    Dg.getDgById = function(data){
        return $http.get(baseURl.apiURL+'/deliveryguy/'+data+'/').then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    Dg.getAttendance =  function(date){
        return $http.get(baseURl.apiURL+'/deliveryguy/all_dg_attendance/?date='+date).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    Dg.getAttendanceById = function(id,date){
        return $http.post(baseURl.apiURL+'/deliveryguy/'+id+'/attendance/',date).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    Dg.deleteDg = function(id){
        Errorhandler.clear();
        return $http.delete(baseURl.apiURL+'/deliveryguy/'+id+'/').then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };
    return Dg;
});

ygVendors.factory('GetJsonData', function ($http,$q,baseURl,StoreSession,$localStorage){
    var GetJsonData = {};

    GetJsonData.fetchFromServer = function(){
        var jsonData = {};
        var deferred =  $q.defer();

        var getvendor = $http.get(baseURl.V2apiURL+'/vendor/');
        var dg = $http.get(baseURl.apiURL+'/deliveryguy/');
        $q.all([getvendor,dg]).then(function (value){
            jsonData.vendors = value[0].data;
            jsonData.dgs = value[1].data;
            deferred.resolve(jsonData);
        }, function (error){
            deferred.reject("Could not retrieve data! Please reload the page"+error);
        });

        return deferred.promise;
    };
    return GetJsonData;
});

ygVendors.factory('Dashboard', function ($http,baseURl,Errorhandler){
    var dashboard = {};
    dashboard.getData = function(data){
        return $http.post(baseURl.V2apiURL+"/dashboard_report/",data).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    dashboard.getExcelData = function(data){
        return $http.post(baseURl.V2apiURL+"/excel_download/",data).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };
    return dashboard;
});

ygVendors.factory('Complaints', function ($http,$q,baseURl,Errorhandler){
    var complaints = {};

    complaints.getTicketAndGroup = function(){
        var jsonData = {};
        var deferred =  $q.defer();
        var getticket =  $http.get(baseURl.apiURL+"/freshdesk/all_tickets/");
        var getgroup =  $http.get(baseURl.apiURL+"/freshdesk/groups/");
        $q.all([getticket,getgroup]).then(function (value){
            jsonData.tickets = value[0].data;
            jsonData.groups = value[1].data;
            deferred.resolve(jsonData);
        }, function (error){
            deferred.reject("Could not retrieve data! Please reload the page");
        });

        return deferred.promise;
    };

    complaints.getTicketByIdAndGroup = function(id){
        var jsonData = {};
        var deferred =  $q.defer();
        var getticket =  $http.get(baseURl.apiURL+"/freshdesk/get_ticket?ticket_id="+id);
        var getgroup =  $http.get(baseURl.apiURL+"/freshdesk/groups/");
        $q.all([getticket,getgroup]).then(function (value){
            jsonData.ticket_with_id = value[0].data;
            jsonData.groups = value[1].data;
            deferred.resolve(jsonData);
        }, function (error){
            deferred.reject("Could not retrieve data! Please reload the page");
        });

        return deferred.promise;
    };
    
    complaints.getTickets = function(){
        return $http.get(baseURl.apiURL+"/freshdesk/all_tickets/").then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    complaints.getGroups =  function(){
        return $http.get(baseURl.apiURL+"/freshdesk/groups/").then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    complaints.creatTickets = function(data){
        return $http.post(baseURl.apiURL+"/freshdesk/create_ticket/",data).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    complaints.getTicketById = function(id){
        return $http.get(baseURl.apiURL+"/freshdesk/get_ticket?ticket_id="+id).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    complaints.addNotes = function(data){
        return $http.post(baseURl.apiURL+"/freshdesk/add_note/",data).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    complaints.closeComplain = function(data){
        return $http.post(baseURl.apiURL+"/freshdesk/resolve/",data).then(Errorhandler.successStatus,Errorhandler.errorStatus);
    };

    return complaints;
});

ygVendors.factory('StoreSessionData', function (){
    var sessionData = {};
    var StoreSessionData = {};

    StoreSessionData.setData = function(name, data){
        sessionData[name] = data;
    };

    StoreSessionData.getData = function(name){
        return sessionData[name];
    };

    StoreSessionData.clearData = function(name){
        delete  sessionData[name];
    };

    StoreSessionData.returnGruopName = function(id){
        if(sessionData.ticket_gruops){
            for(var i=0 ; i< sessionData.ticket_gruops.length;i++){
                if(id == sessionData.ticket_gruops[i].group.id){
                    return sessionData.ticket_gruops[i].group.name;
                }
            }
        }
    };

    return StoreSessionData;
});
