angular.module('development',[]).constant('baseURl',{
  apiURL:'http://127.0.0.1'
});

angular.module('stage',[]).constant('baseURl',{
  apiURL:'/api/v1'
  ,V2apiURL:'/api/v2'
  ,VENDOR:'vendor'
  ,OPS:'operations'
  ,STATUS : {
    INTRANSIT :'INTRANSIT'
    ,QUEUED: 'QUEUED'
    ,DELIVERED:'DELIVERED'
    ,ORDER_PLACED:'ORDER_PLACED'
    ,PICKUPATTEMPTED : 'PICKUPATTEMPTED'
    ,DELIVERYATTEMPTED : 'DELIVERYATTEMPTED'
    ,CANCELLED : 'CANCELLED'
    ,REJECTED : 'REJECTED'
  }
  ,STATUS_OBJECT : [
    {status:'Intransit',value:'INTRANSIT',selected:false}
    ,{status:'Queued',value:'QUEUED',selected:false}
    ,{status:'Delivered',value:'DELIVERED',selected:false}
    ,{status:'Order Placed',value:'ORDER_PLACED',selected:false}
    ,{status:'Pickup Attempted',value:'PICKUPATTEMPTED',selected:false}
    ,{status:'Deliver Attempted',value:'DELIVERYATTEMPTED',selected:false}
    ,{status:'Cancelled',value:'CANCELLED',selected:false}
    ,{status:'Rejected',value:'REJECTED',selected:false}
  ]
  ,ROLE:{
    dg:'deliveryguy'
  }
  ,MARKER : '/static/webapp/images/Map.png'
  ,MARKER_BIKER_AVAIL : '/static/webapp/images/map_icon_biker_available.png'
  ,MARKER_BIKER_BUSY : '/static/webapp/images/map_icon_biker_busy.png'
  ,MARKER_WALKER_AVAIL : '/static/webapp/images/map_icon_walker_available.png'
  ,MARKER_WALKER_BUSY : '/static/webapp/images/map_icon_walker_busy.png'
  ,ItemByPage : 50
  ,ACCESS_KEY : 'AKIAJTRSKA2PKKWFL5PA'
  ,SECRET_KEY : 'grJpBB1CcH8ShN6g88acAkDjvklYdgX7OENAx4g/'
  ,S3_BUCKET : 'yourguy-pod-test'
});

angular.module('production',[]).constant('baseURl',{
  apiURL:'/api/v1'
  ,V2apiURL:'/api/v2'
  ,VENDOR:'vendor'
  ,OPS:'operations'
  ,STATUS : {
    'INTRANSIT' :'Intransit'
    ,'QUEUED': 'Queued'
    ,'DELIVERED':'Delivered'
    ,'ORDER_PLACED':'Order Placed'
    ,'PICKUPATTEMPTED' : 'Pickup Attempted'
    ,'DELIVERYATTEMPTED' : 'Deliver Attempted'
    ,'CANCELLED' : 'Cancelled'
    ,'REJECTED' : 'Rejected'
  }
  ,STATUS_OBJECT : [
    {status:'Intransit',value:'INTRANSIT'}
    ,{status:'Queued',value:'QUEUED',selected:false,selected:false}
    ,{status:'Delivered',value:'DELIVERED',selected:false}
    ,{status:'Order Placed',value:'ORDER_PLACED',selected:false}
    ,{status:'Pickup Attempted',value:'PICKUPATTEMPTED',selected:false}
    ,{status:'Deliver Attempted',value:'DELIVERYATTEMPTED',selected:false}
    ,{status:'Cancelled',value:'CANCELLED',selected:false}
    ,{status:'Rejected',value:'REJECTED',selected:false}
  ]
  ,ROLE:{
    dg:'deliveryguy'
  }
  ,MARKER : '/static/webapp/images/Map.png'
  ,MARKER_BIKER_AVAIL : '/static/webapp/images/map_icon_biker_available.png'
  ,MARKER_BIKER_BUSY : '/static/webapp/images/map_icon_biker_busy.png'
  ,MARKER_WALKER_AVAIL : '/static/webapp/images/map_icon_walker_available.png'
  ,MARKER_WALKER_BUSY : '/static/webapp/images/map_icon_walker_busy.png'
  ,ItemByPage : 50
  ,ACCESS_KEY : 'AKIAJTRSKA2PKKWFL5PA'
  ,SECRET_KEY : 'grJpBB1CcH8ShN6g88acAkDjvklYdgX7OENAx4g/'
  ,S3_BUCKET : 'yourguy-pod'
});

var ygVendors = angular.module('ygwebapp',['ui.router','ngCookies','ngStorage','ngAnimate','cfp.loadingBar',
  'base64','smart-table','ui.bootstrap','gm.datepickerMultiSelect','ng-fusioncharts','ngMaterial','production'
]);

ygVendors.run(function ($rootScope, $location, $state, $localStorage,$templateCache) {
  $rootScope.$on('$stateChangeStart', function (event, toState, toParams ,fromState, fromParams){
    var requireLogin = toState.data.requireLogin;

    if(requireLogin && $localStorage.token === undefined || requireLogin && $localStorage.username === undefined ){
      delete $localStorage.username
      delete $localStorage.token
      $location.path('/login');
    }
    else if(!requireLogin && $localStorage.token != undefined && $localStorage.username != undefined){
      $location.path('/home/order');
    }
    else{
      if(fromState.name == '' && fromState.url == '^'){
        delete $localStorage.customers
      // $templateCache.removeAll();
      }

      if (toState.name == 'home.order'){
        var templateUrl = ($localStorage.username == 'operations') ? 'new_order' : 'order'
        toState.controller = ($localStorage.username == 'operations') ? 'newOrderCntrl' : 'orderCntrl'
        toState.templateUrl = '/static/webapp/partials/'+templateUrl+'.html';
      }
    }
  });
})

ygVendors.config(function ($stateProvider, $urlRouterProvider, $httpProvider,cfpLoadingBarProvider){
  cfpLoadingBarProvider.includeSpinner = false;
  $httpProvider.interceptors.push(function ($q,$location, $localStorage,StoreSession,Errorhandler) {
   return {
     'request': function (config) {
       config.headers = config.headers || {};
       if ($localStorage.token) {
         config.headers.Authorization = 'Token ' + $localStorage.token;
       }
       return config;
     },
     'responseError': function (response) {
      if (response.status === 401 || response.status === 403) {
        StoreSession.destroy();
        $location.path('/');
      }
      return $q.reject(response);     
    }
  };
  });

  $urlRouterProvider.otherwise("/");
  $stateProvider
  .state('login', {
    url: "/",
    templateUrl: "/static/webapp/partials/signin.html",
    controller: "loginCntrl",
    data :{
      requireLogin:false
    }
  })
  .state('signup', {
    url: "/signup",
    templateUrl: "/static/webapp/partials/signup.html",
    controller: "signupCntrl",
    data :{
      requireLogin:false
    }
  })
  .state('tc', {
    url: "/tc",
    templateUrl: "/static/webapp/partials/tc.html",
    data :{
      requireLogin:false
    }
  })
  .state('home', {
    url: "/home",
    abstract:true,
    templateUrl: "/static/webapp/partials/home.html",
    controller: "homeCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.order', {
    url: "/order?date&vendor&dg&status&start_time&end_time&cod&page&search",
    reloadOnSearch : false,
    data :{
      requireLogin:true
    }
  })
  .state('home.user', {
    url: "/user?page&search",
    templateUrl: "/static/webapp/partials/user.html",
    reloadOnSearch : false,
    controller: "userCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.create_order', {
    url: "/order/create",
    templateUrl: "/static/webapp/partials/place-order.html",
    controller: "createOrderCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.create_user', {
    url: "/user/create",
    templateUrl: "/static/webapp/partials/customer-form.html",
    controller: "createUserCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.product', {
    url: "/product",
    templateUrl: "/static/webapp/partials/product.html",
    controller: "productCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.create_product', {
    url: "/product/create",
    templateUrl: "/static/webapp/partials/product-form.html",
    controller: "createProductCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.order_details', {
    url: "/order/:orderId&:dateId",
    templateUrl: "/static/webapp/partials/order_details.html",
    controller: "orderDetailsCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.dg', {
    url: "/dg?date&page&attendance&search",
    reloadOnSearch : false,
    templateUrl: "/static/webapp/partials/dg.html",
    controller: "dgCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.create_dg', {
    url: "/dg/create",
    templateUrl: "/static/webapp/partials/dg-form.html",
    controller: "createDgCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.dg_details', {
    url: "/dg/:dgId",
    templateUrl: "/static/webapp/partials/dg-details.html",
    controller: "dgDetailsCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.vendor', {
    url: "/vendor",
    templateUrl: "/static/webapp/partials/vendor.html",
    controller: "vendorCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.vendor_details', {
    url: "/vendor/:vendorId",
    templateUrl: "/static/webapp/partials/vendor-details.html",
    controller: "vendorDetailsCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.customer_details', {
    url: "/user/:customerId",
    templateUrl: "/static/webapp/partials/customer-details.html",
    controller: "customerDetailsCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.account', {
    abstract: true,
    templateUrl: "/static/webapp/partials/account.html",
    data :{
      requireLogin:true
    }
  })
  .state('home.account.settings', {
    url: "/account/settings",
    templateUrl: "/static/webapp/partials/account-settings.html",
    controller: "accountSettingCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.file_upload', {
    url: "/upload",
    templateUrl: "/static/webapp/partials/file-upload.html",
    controller: "fileUploadCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.reports', {
    url: "/reports",
    templateUrl: "/static/webapp/partials/reports.html",
    controller: "reportsCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.complaints', {
    url: "/complaints",
    templateUrl: "/static/webapp/partials/complaints.html",
    controller: "complaintsCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.create_complaints', {
    url: "/complaints/create",
    templateUrl: "/static/webapp/partials/create_complaints.html",
    controller: "createComplaintsCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.complain_details', {
    url: "/complaints/:id",
    templateUrl: "/static/webapp/partials/complain_details.html",
    controller: "detailComplaintsCntrl",
    data :{
      requireLogin:true
    }
  })
  .state('home.tutorial', {
    url: "/tutorial",
    templateUrl: "/static/webapp/partials/tutorial.html",
    controller: "tutorialCntrl",
    data :{
      requireLogin:true
    }
  })
})

ygVendors.controller('loginCntrl',function ($scope,$http,AuthService,StoreSession,$location,$base64){
  var success = function(data){
    var token = data.auth_token
    var username = $base64.decode(token);
    username = username.split(':')
    if(token != undefined && username[1] != undefined){
      StoreSession.create(token,username[1])
      $location.path('/home/order')
    }
    else{
      $scope.login_in_process = false
      $scope.loginError = true
      $scope.err_invalid_Msg = "Access Denied"
    }
  }

  $scope.processLogin = function(){
    $scope.loginError = false
    $scope.login_in_process = true
    $scope.err_invalid_Msg = null
    $scope.err_pass_Msg = null
    $scope.err_user_Msg = null

    AuthService.login($scope.login_cred,success,function (err){
      $scope.login_in_process = false
      $scope.loginError = true
      if(err.non_field_errors){
        $scope.err_invalid_Msg = err.non_field_errors[0]
      }
      else if(err.password && !err.username){
        $scope.err_pass_Msg = err.password[0]
      }
      else {
        $scope.err_user_Msg = err.username[0]
      }

    })
  }
})

ygVendors.controller('signupCntrl',function ($scope,$http,$state,AuthService,Codes,Errorhandler,$timeout){
  $scope.getAreCode =  function(){
    Codes.getAreCode().then(function (response){
      if(response.status === 200){
        $scope.area_codes = response.data
      }
    },function (response){
      if(response.status!= 200){
        $scope.errmsg = "Error getting area codes, Please refresh the page"
      }
    })
  }();

  $scope.register = function(){
    $scope.signup_in_process = true
    $scope.errmsg = null;
    AuthService.signup($scope.signup).finally(function(){
      $scope.signup_in_process = false
      var status = Errorhandler.getStatus()
      if(status.has_error){
        $scope.errmsg = status.error
      }
      else{
        $scope.success_msg = status.data.status
        $scope.show_success_msg = true
        $timeout(function() {
         $state.go('login')
       }, 3000);
      }
    })
  }
})

ygVendors.controller('homeCntrl', function ($state,$scope,StoreSession,$q,$modal,GetJsonData,DG,Vendors,Codes,baseURl,Errorhandler){
  Date.prototype.addHours= function(h){
    this.setHours(this.getHours()+h);
    this.setMinutes(0)
    return this;
  }

  Date.prototype.addActlHours = function(h) {    
   this.setTime(this.getTime() + (h*60*60*1000)); 
   return this;   
  }

  Date.prototype.subbActlHours = function(h) {    
   this.setTime(this.getTime() - (h*60*60*1000)); 
   return this;   
  }

  Date.prototype.setCustomHours = function(h){
    this.setHours(h)
    this.setMinutes(0)
    return this;
  }

  $scope.open_sidebar = false;
  $scope.role = {}

  $scope.logout = function(){
    StoreSession.destroy()
    $state.go('login')
  }

  $scope.openModal =  function(){
    var modalInstance =  $modal.open({
      templateUrl:'/static/webapp/partials/modals/confirmModal.html',
      controller:'modalConfirmCntrl',
      backdropClass : 'modal_back',
      windowClass :'modal_front',
      resolve : {
        details: function () {
          var object = {}
          object.modal_scope = 'logout'
          return object;
        }
      }
    })

    modalInstance.result.then(function (data) {
      $scope.logout()
    }, function () {
      console.log("Closed")
    });
  }

  $scope.hideSidebar = function(){
    if($state.current.name == 'home.account.settings'){
      $scope.account_active = true
    }
    else{
       $scope.account_active = false
    }
    $scope.open_sidebar = false;
  }

  var error = function(data){
    alert(data)
  }

  $scope.getUsername = function(){
    var username = StoreSession.getUsername()
    if(username == baseURl.OPS){
      $scope.role.ops = true
      $scope.user ={}
      $scope.user.name  = baseURl.OPS.toUpperCase()
      GetJsonData.fetchFromServer().then(function (data){
        $scope.vendors = data.vendors.data;
        $scope.area_codes = data.areas;
        $scope.dgs = data.dgs;
        $scope.dgs.unshift({user :{username:'UNASSIGNED',first_name:'Unassigned'}})
        $scope.dgs.unshift({user :{username:'UNASSIGNED_DELIVERY',first_name:'Unassigned Delivery'}})
        $scope.dgs.unshift({user :{username:'UNASSIGNED_PICKUP',first_name:'Unassigned Pickup'}})
      },error)
    }
    else if(username == baseURl.VENDOR){
      $scope.role.vendor = true
      GetJsonData.fetchFromServer().then(function (data){
        $scope.user  = data.vendors.data;
      },error)
    } 
  }
  $scope.getUsername()
})

ygVendors.controller('newOrderCntrl',function ($scope,$stateParams,$state,$location,$modal,cfpLoadingBar,Orders,baseURl,Errorhandler,$timeout){
  $scope.order_template =($scope.$parent.role.ops) ? 'new_order' : 'order';
  $scope.format = 'dd/MM/yyyy'
  $scope.itemsByPage = baseURl.ItemByPage
  $scope.notification = {}
  $scope.notification.type = null
  $scope.notification.message = null
  $scope.STATUS = baseURl.STATUS_OBJECT
  $scope.order_params = $stateParams
  $scope.order_params.date =($stateParams.date!= undefined) ? new Date($stateParams.date) : new Date();
  $scope.order_params.vendor = (!isNaN($stateParams.vendor))? parseInt($stateParams.vendor): undefined;
  $scope.order_params.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
  $scope.order_params.status = ($stateParams.status)? $stateParams.status: [];
  $scope.order_params.cod = ($stateParams.cod == 'true')? Boolean($stateParams.cod): false;
  if(typeof $scope.order_params.status == 'string'){
    $scope.order_params.status = [$scope.order_params.status]
  }
  $scope.order_params.status.forEach(function(status){
    for(var i=0;i<$scope.STATUS.length;i++){
      if(status == $scope.STATUS[i].value){
        $scope.STATUS[i].selected = true
      }
    }
  })
  
  $scope.searched_id = ($stateParams.search != undefined) ? $stateParams.search : null;
  $scope.assign_order = {}
  $scope.assign_order.order_ids = []
  $scope.time_data = [
    {
      value : "00 AM - 06 AM ",
      time: {
        start_time: 1,
        end_time:6
      }
    },
    {
      value : "06 AM - 12 PM",
      time: {
        start_time: 6,
        end_time:12
      }
    },
    {
      value : "12 PM - 06 PM",
      time: {
        start_time: 12,
        end_time:18
      }
    },
    {
      value : "06 PM - 12 AM",
      time: {
        start_time: 18,
        end_time:23
      }
    }
  ]

  $scope.startopen = function($event) {
    $event.preventDefault();
    $event.stopPropagation();
    $scope.opened = true;
  };

  $scope.search_order = function(id){
    if(id == undefined || id == ""){
      delete $scope.order_params.search 
    }
    else{
      $scope.order_params.search = id
    }
  }

  $scope.compareCOD = function(order){
    if(order.cod_collected == order.cod_amount){
      return 'success-text'
    }
    else{
      return 'danger-text'
    }
  }

  $scope.hideNotificationBar = function(){
    $scope.notification.type = null
    $scope.notification.message = null
  }

  var filterApplied = function(){
    if($scope.order_params.status.length != 0|| $scope.order_params.vendor != undefined  || $scope.order_params.dg != undefined || $scope.order_params.search != undefined || $scope.order_params.end_time != undefined || $scope.order_params.start_time != undefined){
      return true
    }
    else{
      return false
    }
  }

  $scope.redirect_to_details = function(order){
    $state.go('home.order_details',{orderId:order.id,dateId: new Date($scope.order_params.date).toISOString()})
  }

  $scope.error_handler= function(type,message){
    $scope.notification.type = type
    $scope.notification.message = message
    $timeout(function(){
      $scope.hideNotificationBar()
    },5000)
  }

  $scope.reset_filter = function(){
    $scope.order_params.vendor = undefined
    $scope.order_params.dg = undefined
    $scope.order_params.page = 1
    $scope.order_params.search = undefined
    $scope.searched_id = null
    $scope.order_params.start_time = undefined
    $scope.order_params.end_time = undefined
    $scope.order_time = null
    $scope.order_params.cod = undefined
    $scope.order_params.status = []
    $scope.unselectOrderStatus()
  }

  $scope.selectOrderStatus = function(object){
    $scope.st = false
    if(object.selected){
      $scope.order_params.status.push(object.value)
    }
    else{
      var index = $scope.order_params.status.indexOf(object.value);
      $scope.order_params.status.splice(index,1)
    }
  }

  $scope.unselectOrderStatus = function(){
    $scope.st = true
    $scope.order_params.status = []
    $scope.STATUS.forEach(function(status){
      status.selected = false
    })
    $scope.show_status = false
  }

  $scope.selectTime = function(time){
    if(time){
      $scope.order_params.start_time = time.start_time
      $scope.order_params.end_time = time.end_time
    }
    else{
      $scope.order_params.start_time = null
      $scope.order_params.end_time = null
    }
  }

  $scope.getOrder = function(data){
    var params_for_orders = angular.copy(data)
    params_for_orders.date = params_for_orders.date.toISOString()
    params_for_orders.status = data.status.toString()
    if(data.start_time && data.end_time){
      params_for_orders.start_time = new Date()
      params_for_orders.start_time.setHours(data.start_time)
      params_for_orders.start_time.setMinutes(0)
      params_for_orders.start_time = params_for_orders.start_time.toISOString()
      params_for_orders.end_time = new Date()
      params_for_orders.end_time.setHours(data.end_time)
      params_for_orders.end_time.setMinutes(0)
      params_for_orders.end_time = params_for_orders.end_time.toISOString()
    }
    cfpLoadingBar.start();
    Orders.fetchOrderForDate(params_for_orders).finally(function(){
      var status = Errorhandler.getStatus()
      $scope.order_not_found = undefined
      $scope.total_orders = false
      cfpLoadingBar.complete();
      if(status.has_error){
        $scope.error_handler('error',status.error)
      }
      else if(status.data.total_orders == 0){
        if(filterApplied()){
          $scope.order_not_found = 'no-orders-filter'
        }
        else{
          $scope.order_not_found = 'no-orders-ops'
        }
      }
      else{
        $scope.orders_data = status.data.data
        $scope.total_orders = status.data.total_orders
        $scope.orders_data.forEach(function (order){
          if($scope.assign_order.order_ids.indexOf(order.id) != -1){
              order.selected = true
          }
          else{
           order.selected = false
          }
        })
      }
    })
  }

  $scope.$watch('order_params', function (newValue,oldValue){
    if(newValue){
      if (parseInt(newValue.page) == parseInt(oldValue.page)) {newValue.page = 1}
      $location.search(newValue)
      $scope.getOrder(newValue)
    }
  },true)

  $scope.select_all_order =  function(data){
    if(data){
      $scope.orders_data.forEach(function (order){
        order.selected = data
        $scope.assign_order.order_ids.push(order.id)
      })
    }
    else if(!data){
      $scope.orders_data.forEach(function (order){
        order.selected = data
      })
      $scope.assign_order.order_ids = []
    }
  }

  $scope.select_single_order = function(order){
    if(order.selected){
      $scope.assign_order.order_ids.push(order.id)
    }
    else{
      $scope.assign_order.order_ids.splice($scope.assign_order.order_ids.indexOf(order.id),1)
    }
  }

  $scope.$watch(function ($scope){return $scope.assign_order.order_ids.length},
    function (newValue,oldValue){
      if(newValue == 0){
        $scope.is_selected = false
      }
      else if(newValue > 0){
        $scope.is_selected = true
      }
    }
  )

  $scope.assign_dgs = function(dg_array){
    for(var i = dg_array.length -1; i >= 0 ; i--){
      if(dg_array[i].dg_id){
        dg_array[i].order_ids = $scope.assign_order.order_ids,
        dg_array[i].date = new Date($scope.order_params.date).toISOString()
      }
      else{
        dg_array.splice(i, 1);
      }
    }
    if(dg_array.length > 0){
      cfpLoadingBar.start();
      Orders.assignOrder(dg_array).then(function (data){
        cfpLoadingBar.complete();
        $scope.error_handler('success','Orders assigned successfully')
        $scope.assign_order.order_ids = []
        $scope.is_all_selected = false
        $scope.getOrder($scope.order_params)
      },function (err){
        cfpLoadingBar.complete();
        $scope.assign_order.order_ids = []
        $scope.error_handler('error',err)
      })
    }
  }

  $scope.asignSingleOrder = function(order){
    $scope.assign_order.order_ids.push(order.id)
    $scope.openDgModal(order.pickupguy_id,order.deliveryguy_id)
  }

  $scope.openDgModal =  function(pickupguy,deliveryguy){
    var modalInstance =  $modal.open({
      templateUrl:'/static/webapp/partials/modals/dgAssignModal.html?nd=' + Date.now(),
      controller:'modalDgCntrl',
      backdropClass : 'modal_back',
      windowClass :'modal_front',
      resolve : {
        details: function () {
          var object = {}
          object.dgs = $scope.$parent.dgs
          object.pickupguy = pickupguy
          object.deliveryguy = deliveryguy
          return object;
        }
      }
    })

    modalInstance.result.then(function (data) {
       $scope.assign_dgs(data)
    }, function () {
      console.log("Closed")
    });
  }

  $scope.changeOrderStatus = function(status){
    cfpLoadingBar.start();
    if(status.name == 'intransit'){
      var pickup_datetime = new Date()
      pickup_datetime.setDate($scope.order_params.date.getDate())
      pickup_datetime.setMonth($scope.order_params.date.getMonth())
      pickup_datetime = pickup_datetime.toISOString()
      status.order_to_update.forEach(function (order){
        order.date = pickup_datetime
      })
      Orders.updateIntransitStatus(status.order_to_update).then(function(data){
        $scope.assign_order.order_ids = []
        $scope.is_all_selected = false
        $scope.getOrder($scope.order_params)
      },
      function (err){
        cfpLoadingBar.complete();
        $scope.error_handler('error',err)
      })
    }
    else if(status.name == 'delivered'){
      var delivered_datetime = new Date()
      delivered_datetime.setDate($scope.order_params.date.getDate())
      delivered_datetime.setMonth($scope.order_params.date.getMonth())
      delivered_datetime = delivered_datetime.toISOString()
      status.order_to_update.forEach(function (order){
        order.date = delivered_datetime
      })
      Orders.updateDeliveredStatus(status.order_to_update).then(function(data){
        $scope.assign_order.order_ids = []
        $scope.is_all_selected = false
        $scope.getOrder($scope.order_params)
      },
      function (err){
        cfpLoadingBar.complete();
        $scope.error_handler('error',err)
      })
    }
  }

  $scope.selectStatus = function(){
    if($scope.assign_order.order_ids.length > 10){
      return alert('Please select less than 10 orders')
    }
    else{
      var modalInstance =  $modal.open({
        templateUrl:'/static/webapp/partials/modals/orderStatusModal.html?nd=' + Date.now(),
        controller:'orderStatusCntrl',
        backdropClass : 'modal_back',
        windowClass :'modal_front',
        resolve : {
          details: function () {
            var object = {}
            object.order_ids = $scope.assign_order.order_ids
            return object;
          }
        }
      })
      modalInstance.result.then(function (data) {
         $scope.changeOrderStatus(data)
       }, function () {
        console.log("Closed")
      });
    }
  }
})

ygVendors.controller('orderCntrl',function ($scope,$state,$stateParams,cfpLoadingBar,$timeout,$location,$modal,StoreSession,Orders,baseURl,Errorhandler,DG,Vendors){
  $scope.toggle = false
  $scope.oders_data = []
  $scope.itemsByPage = baseURl.ItemByPage
  $scope.STATUS = baseURl.STATUS_OBJECT
  $scope.format = 'dd-MMMM-yyyy'
  $scope.notification = {}
  $scope.order_params = $stateParams
  $scope.searched_id = ($stateParams.search != undefined) ? $stateParams.search : undefined;
  $scope.order_params.date =($stateParams.date!= undefined) ? new Date($stateParams.date) : new Date();
  $scope.order_params.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
  $scope.order_params.status = ($stateParams.status)? $stateParams.status: [];
  if(typeof $scope.order_params.status == 'string'){
    $scope.order_params.status = [$scope.order_params.status]
  }
  $scope.order_params.status.forEach(function(status){
    for(var i=0;i<$scope.STATUS.length;i++){
      if(status == $scope.STATUS[i].value){
        $scope.STATUS[i].selected = true
      }
    }
  })

  $scope.hideNotificationBar = function(){
    $scope.notification.type = null
    $scope.notification.message = null
  }

  $scope.error_handler= function(type,message){
    $scope.notification.type = type
    $scope.notification.message = message
    $timeout(function(){
      $scope.hideNotificationBar()
    },5000)
  };

  $scope.compareCOD = function(order){
    if(order.cod_collected == order.cod_amount){
      return 'success-text'
    }
    else{
      return 'danger-text'
    }
  };

  var filterApplied = function(){
    if($scope.order_params.status.length != 0 || $scope.order_params.search != undefined ){
      return true
    }
    else{
      return false
    }
  }

  $scope.selectOrderStatus = function(object){
    object.selected = !object.selected
    $scope.show_status = false
    $scope.st = false
    if(object.selected){
      $scope.order_params.status.push(object.value)
    }
    else{
      var index = $scope.order_params.status.indexOf(object.value);
      $scope.order_params.status.splice(index,1)
    }
  }

  $scope.unselectOrderStatus = function(){
    $scope.st = true
    $scope.order_params.status = []
    $scope.STATUS.forEach(function(status){
      status.selected = false
    })
    $scope.show_status = false
  }

  $scope.getOrder = function(data){
    var params_for_orders = angular.copy(data)
    params_for_orders.date = params_for_orders.date.toISOString()
    params_for_orders.status = data.status.toString()
    cfpLoadingBar.start();
    Orders.fetchOrderForDate(params_for_orders).finally(function(){
      var status = Errorhandler.getStatus()
      cfpLoadingBar.complete();
      $scope.order_not_found = undefined
      $scope.total_orders = false
      if(status.has_error){
        $scope.error_handler('error',status.error)
      }
      else if(status.data.total_orders == 0){
        if(filterApplied()){
          $scope.order_not_found = 'no-orders-filter'
        }
        else{
          $scope.order_not_found = 'no-orders'
        }
      }
      else{
        $scope.orders_data = status.data.data
        $scope.total_orders = status.data.total_orders
        $scope.orders_data.forEach(function (order){
          if($scope.assign_order.order_ids.indexOf(order.id) != -1){
              order.selected = true
          }
          else{
           order.selected = false
          }
        })
      }
    })
  }

  $scope.diplay_orders = [].concat($scope.orders_data)

  $scope.$watch('order_params', function (newValue,oldValue){
    if(newValue){
      if (parseInt(newValue.page) == parseInt(oldValue.page)){
        newValue.page = 1
      }
      $location.search(newValue)
      $scope.getOrder(newValue)
    }
  },true)

  $scope.search_order = function(id){
    if(id == undefined || id == ""){
      delete $scope.order_params.search 
    }
    else{
      $scope.order_params.search = id
    }
  }

  $scope.startopen = function($event) {
    $event.preventDefault();
    $event.stopPropagation();
    $scope.opened = true;
  };

  $scope.redirect_to_details = function(order){
    $state.go('home.order_details',{orderId:order.id,dateId: new Date($scope.order_params.date).toISOString()})
  }
})

ygVendors.controller('createOrderCntrl',function ($scope,$state,$modal,$timeout,$filter,Orders,Products,Consumers,cfpLoadingBar,Errorhandler){
  $scope.format = 'dd/MM/yyyy'
  $scope.notification = {}
  $scope.notification.type = null
  $scope.notification.message = null
  $scope.accordian = {
    customer: true,
    order:true
  }
  $scope.datePicker = {}
  $scope.order_data = {}
  $scope.create_params = {}
  $scope.create_params.consumers = []
  $scope.create_params.recurring = {}
  $scope.create_params.recurring.by_day = []
  $scope.week = [
    {value:false,day:"MO"},
    {value:false,day:"TU"},
    {value:false,day:"WE"},
    {value:false,day:"TH"},
    {value:false,day:"FR"},
    {value:false,day:"SA"},
    {value:false,day:"SU"},
  ]

  $scope.hideNotificationBar = function(){
    $scope.notification.type = null
    $scope.notification.message = null
  }

  $scope.error_handler= function(type,message){
    $scope.notification.type = type
    $scope.notification.message = message
    $timeout(function(){
      $scope.hideNotificationBar()
    },5000)
  }

  $scope.$watch('order_data.search_customer',function (newValue,oldValue){
    if(newValue){
      $scope.order_data.searching = true
      Orders.searchCustomer(newValue).finally(function(){
        var status = Errorhandler.getStatus()
        $scope.order_data.searching = false
        if(status.data.data.length == 0){
          $scope.order_data.searched_customer = [{ name: 'No results found'}]
        }
        else{
          $scope.order_data.searched_customer = status.data.data
        }
      })
    }
  })

  $scope.CheckAddress =  function(customer){
    if(customer.address_id == null){
      $scope.openAddressModal(customer)
    }
  }

  $scope.selectCustomer = function(cust){
    if(cust.name =='No results found'){
      return;
    }
    cust.address_id = cust.addresses[0].id
    $scope.create_params.consumers.push(cust)
    $scope.order_data.search_customer = null
  }

  $scope.removeCustomer = function(cust){
    var index = $scope.create_params.consumers.indexOf(cust);
    $scope.create_params.consumers.splice(index,1)
  }

  $scope.selectTimeSlot = function(){
    $scope.create_params.product_id = $scope.order_data.selected_product.id
    $scope.order_data.timeslots = $scope.order_data.selected_product.timeslots
  }

  $scope.getProduct = function(){
    cfpLoadingBar.start();
    Products.getProduct().finally(function(){
      var status = Errorhandler.getStatus()
      cfpLoadingBar.complete();
      if(status.has_error){
        $scope.error_handler('error',status.error)
      }
      else{
        $scope.order_products = status.data.products
        $scope.order_data.products = $scope.order_products
      }
    })
  }()

  $scope.orderDateOpen = function($event) {
    $event.preventDefault();
    $event.stopPropagation();
    $scope.datePicker.orderDateOpen = true;
  };

  $scope.startOpen = function($event) {
    $event.preventDefault();
    $event.stopPropagation();
    $scope.datePicker.startOpen = true;
  };

  $scope.endOpen = function($event) {
    $event.preventDefault();
    $event.stopPropagation();
    $scope.datePicker.endOpen = true;
  };

  $scope.selectDays = function(object){
    if(object.value){
      $scope.create_params.recurring.by_day.push(object.day)
    }
    else{
      var index = $scope.create_params.recurring.by_day.indexOf(object.day);
      $scope.create_params.recurring.by_day.splice(index,1)
    }
  }

  $scope.openCustModal = function(){
    var custModalInstance =  $modal.open({
      templateUrl:'/static/webapp/partials/modals/addCustomerModal.html',
      controller:'addCustomerPopup',
      backdropClass : 'modal_back',
      windowClass :'modal_front',
      resolve : {
        details: function () {
          var object = {}
          object.area_codes = $scope.$parent.area_codes
          return object;
        }
      }
    })

    custModalInstance.result.then(function (data) {
      $scope.create_params.consumers.push(data)
    }, function () {
      console.log("Closed")
    });
  }

  $scope.openAddressModal =  function(cust){
    var modalInstance =  $modal.open({
      templateUrl:'/static/webapp/partials/modals/addAddress.html',
      controller:'addAddressPopup',
      backdropClass : 'modal_back',
      windowClass :'modal_front',
      resolve : {
        details: function () {
          var object = {}
          object.area_codes = $scope.area_codes
          return object;
        }
      }
    })

    modalInstance.result.then(function (data) {
      cfpLoadingBar.start();
      Consumers.addAddress(cust.id,data).finally(function(){
        var status = Errorhandler.getStatus()
        cfpLoadingBar.complete()
        if(status.has_error){
          $scope.error_handler('error',status.error)
        }
        else{
          data.id = status.data.address_id
          cust.addresses.push(data)
          cust.address_id = status.data.address_id
          $scope.error_handler('success','Address added successfully')
        }
      })
    }, function () {
      console.log("Closed")
    });
  }

  $scope.createOrder = function(){
    $scope.create_params.timeslots = angular.fromJson($scope.create_params.timeslots);
    if(!$scope.create_params.is_recurring){ 
      delete $scope.create_params.recurring 
    }
    else{
      if($scope.create_params.recurring.by_day.length == 0){
        $scope.error_handler('error','Please select the days for recurring order')
        return;
      }
      else if($scope.create_params.recurring.start_date < $scope.create_params.order_date || $scope.create_params.recurring.end_date < $scope.create_params.order_date){
        $scope.error_handler('error','Start date and end date should be greater than order date')
        return;
      }
      else if($scope.create_params.recurring.start_date > $scope.create_params.recurring.end_date){
        $scope.error_handler('error','Start date should be less than end date')
        return;
      }
      else{
        $scope.create_params.recurring.start_date = $scope.create_params.recurring.start_date.addHours(6).toISOString()
        $scope.create_params.recurring.end_date = $scope.create_params.recurring.end_date.addHours(6).toISOString()
      }
    }
    delete $scope.create_params.is_recurring
    $scope.create_params.order_date = $scope.create_params.order_date.addHours(6).toISOString()
    console.log($scope.create_params)
    cfpLoadingBar.start()
    Orders.createOrder($scope.create_params).finally(function(){
      var status = Errorhandler.getStatus()
      cfpLoadingBar.complete()
      if(status.has_error){
        $scope.error_handler('error',status.error)
      }
      else{
        if($scope.order_data.redirect){
          $scope.error_handler('success','Order '+status.data.order_ids.toString()+' created successfully')
          $timeout(function() {
           $state.go('home.order')
          }, 3000);
        }
        else{
          $scope.order_data = {}
          $scope.order_data.products = $scope.order_products
          $scope.create_params = {}
          $scope.create_params.consumers = []
          $scope.create_params.recurring = {}
          $scope.create_params.recurring.by_day = []
          $scope.create_params.vendor_address_id = $scope.$parent.user.addresses[0].id
          $scope.create_params.is_reverse_pickup = false
          $scope.week.forEach(function(data){data.value = false})
          $scope.error_handler('success','Order '+status.data.order_ids.toString()+' created successfully,Please place another order')
        }
      }
    })
  }
})

ygVendors.controller('userCntrl',function ($scope,$http,StoreSession,$location,$stateParams,$modal,cfpLoadingBar,Consumers,Errorhandler,baseURl){
  $scope.toggle = false;
  $scope.open_sidebar = false;
  $scope.user_params = $stateParams;
  $scope.user_params.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
  $scope.searched_cust = $stateParams.search;
  $scope.itemsByPage = baseURl.ItemByPage;

  $scope.search_user = function(id){
    if(id == undefined || id == ""){
      delete $scope.user_params.search; 
    }
    else{
      $scope.user_params.search = id
    }
  };

  $scope.getConsumer = function (data){
    cfpLoadingBar.start()
    Consumers.fetchConsumer(data).finally( function(){
      var get_status = Errorhandler.getStatus()
      cfpLoadingBar.complete()
      if(get_status.has_error){
        $scope.show_consumer_msg = true
        $scope.consumer_msg = get_status.error
      }
      else{
        if(get_status.data.data.length == 0){
          if($scope.user_params.search!= undefined){
            $scope.show_consumer_msg = true
            $scope.consumer_msg = "Sorry! No customer found."
          }
          else{
            $scope.show_consumer_msg = true
            $scope.consumer_msg = "There are no customers. Please start adding your customers."
          }
          
        }
        else{
          $scope.show_consumer_msg = false
          $scope.consumer_data = get_status.data.data
          $scope.totalUsers = get_status.data.total_pages*$scope.itemsByPage
        }
      }
    })
  }

  $scope.display_consumer = [].concat($scope.consumer_data)

  $scope.$watch('user_params', function (newValue,oldValue){
    if(newValue){
      if (parseInt(newValue.page) == parseInt(oldValue.page)) {newValue.page = 1}
      $location.search(newValue);
      $scope.getConsumer(newValue);
    }
  },true)

  $scope.deleteConsumer = function(user){
    $scope.loaded = false
    Consumers.deleteConsumer(user.id).finally(function(){
      var status = Errorhandler.getStatus()
      if(status.has_error){
        $scope.loaded = true
        $scope.show_consumer_msg = true
        $scope.consumer_msg = status.error
        $timeout(function(){
          $scope.getConsumer()
        },3000)
      }
      else{    
        if(StoreSession.getCustomer()){
          StoreSession.removeCustomer(user)
        }
        $scope.getConsumer()
      }
    })
  }

  $scope.openModal =  function(size,user,e){
    e.stopPropagation()
    var modalInstance =  $modal.open({
      templateUrl:'/static/webapp/partials/modals/confirmModal.html?nd=' + Date.now(),
      controller:'modalConfirmCntrl',
      size :size,
      backdropClass : 'modal_back',
      windowClass :'modal_front',
      resolve : {
        details: function () {
          var object = {}
          object.modal_scope = 'delete_customer'
          object.message = "You want to delete customer"
          object.action_on = user
          return object;
        }
      }
    })

    modalInstance.result.then(function (user) {
      $scope.deleteConsumer(user)
    }, function () {
      console.log("Closed")
    });
  }
})

ygVendors.controller('createUserCntrl',function ($scope,Consumers,StoreSession,Codes,$state,$timeout,Errorhandler){
  $scope.createCustomer = function(){
    $scope.customer_in_process = true
    $scope.show_alert_message = false
    $scope.alert_message = null
    Consumers.create($scope.customer).finally(function(){
      $scope.customer_in_process = false
      var get_status = Errorhandler.getStatus()
      if(get_status.has_error == true){
        $scope.show_alert_message = true
        $scope.alert_message = get_status.error;
      }
      else{
        $scope.disable_background = true
        $scope.success_msg = true
        $timeout(function() {
         $state.go('home.user')
        }, 3000);
      }
    })
  }
})

ygVendors.controller('productCntrl',function ($scope,Products,Errorhandler,baseURl){
  $scope.itemsByPage = baseURl.ItemByPage

  $scope.getProduct = function(){
    Products.getProduct().finally(function(){
      $scope.loaded = true
      var status = Errorhandler.getStatus()
      if(status.has_error){
        $scope.show_product_msg = true
        $scope.product_msg = status.error
      }
      else if(status.data.products.length == 0){
        $scope.show_product_msg = true
        $scope.product_msg = "You have no product. Please contact YourGuy to add your products."
      }
      else{
        $scope.show_product_msg = false
        $scope.products = status.data.products
      }
    })
  }()
  $scope.display_product = [].concat($scope.products)
})

ygVendors.controller('createProductCntrl',function ($scope,$state,$timeout,Products,Errorhandler){
  $scope.getCatergory = function(){
    Products.getCategory().finally(function(){
      var status = Errorhandler.getStatus()
      if(status.has_error){
        $scope.show_error_message = true
        $scope.error_msg = status.error
      }
      else{
        $scope.product_category = status.data
        // console.log($scope.product_category)
      }
    })
  }()

  $scope.createProduct = function(){
    $scope.product.vendor = $scope.$parent.user.id
    $scope.product_in_process = true
    $scope.show_error_message = false
    Products.createProduct($scope.product).finally(function(){
      $scope.product_in_process = false
      // console.log(status)
      var status = Errorhandler.getStatus()
      if(status.has_error){
        $scope.show_error_message = true
        $scope.error_msg = status.error
      }
      else{
        $scope.success_msg = true
        $timeout(function() {
          $state.go('home.product')
        }, 3000);
      }
    })  
  }
})

ygVendors.controller('orderDetailsCntrl',function ($scope,$state,$stateParams,$modal,$timeout,cfpLoadingBar,Orders,baseURl,Errorhandler){
  $scope.header = "Order Details"
  $scope.format = 'dd-MMMM-yyyy'
  $scope.notification = {}
  $scope.notification.type = null
  $scope.notification.message = null
  $scope.param = $stateParams
  $scope.accordian = {}
  $scope.accordian.approval = true
  $scope.accordian.order = true
  $scope.accordian.delivery = true
  $scope.accordian.address = true
  $scope.screenWidth = window.innerWidth;
  AWS.config.update({accessKeyId: baseURl.ACCESS_KEY, secretAccessKey: baseURl.SECRET_KEY});
  
  $scope.hideNotificationBar = function(){
    $scope.notification.type = null
    $scope.notification.message = null
  }

  $scope.compareCOD = function(order){
    if(order.cod_collected_amount == order.cod_amount){
      return 'success-text'
    }
    else{
      return 'danger-text'
    }
  }

  var _checkStatus = function(status){
    if(status == 'QUEUED'){
      $scope.order_status = {
        pickup : null,
        deliver : null
      }
    }
    else if(status == 'INTRANSIT'){
      $scope.order_status = {
        pickup : true,
        deliver : null
      }
    }
    else if(status == 'DELIVERED'){
      $scope.order_status = {
        pickup : true,
        deliver : true
      }
    }
    else if(status == 'DELIVERYATTEMPTED' || status == 'ATTEMPTED'){
      $scope.order_status = {
        pickup : true,
        deliver : false
      }
    }
    else if(status == 'PICKUPATTEMPTED'){
      $scope.order_status = {
        pickup : false,
        deliver : null
      }
    }
    else{
      $scope.order_status = {
        pickup : null,
        deliver : null
      }
    }
  }
 
  $scope.getOrderById = function(){
    cfpLoadingBar.start();
    Orders.getOrderById($scope.param).finally(function(){
      var status = Errorhandler.getStatus()
      if(status.has_error){
        cfpLoadingBar.complete()
      }
      else{
        cfpLoadingBar.complete()
        $scope.order_with_id = status.data
        _checkStatus($scope.order_with_id.status)
      }
    })
  }
  $scope.getOrderById()

  $scope.order_approval = function(data){
    cfpLoadingBar.start();
    data.date = $scope.param.dateId
    Orders.approveOrder(data).finally(function(){
      var status = Errorhandler.getStatus()
      cfpLoadingBar.complete()
      if(status.has_error){
        $scope.notification.type = 'error'
        $scope.notification.message = status.error
        $timeout(function(){
          $scope.hideNotificationBar()
        },3000)
      }
      else{
         $scope.getOrderById()
      }
    })
  }

  $scope.openModal =  function(id,message,scope){
    var modalInstance =  $modal.open({
      templateUrl:'/static/webapp/partials/modals/confirmModal.html',
      controller:'modalConfirmCntrl',
      backdropClass : 'modal_back',
      windowClass :'modal_front',
      resolve : {
        details: function () {
          var object = {}
          object.modal_scope = scope
          object.message = "You want to "+message+" the order with Id"
          object.action_on = id
          return object;
        }
      }
    })

    modalInstance.result.then(function (data) {
      if(data.status == 'delete'){
        $scope.deleteOrder(data.order)
      }
      else if(data.status == 'reschedule'){
        $scope.rescheduleOrder(data)
      }
      else{
        $scope.order_approval(data)
      }
    }, function () {
      console.log("Closed")
    });
  }

  $scope.disableByStatus = function(order){
    if(order){
      if(order.status == 'DELIVERED' || order.status == 'ATTEMPTED' || order.status == 'CANCELLED'|| order.status == 'REJECTED'){
        return true;
      }
      else{
        return false;
      }
    }
  }

  $scope.downloadPop = function(){ 
    var param = {
      Bucket : baseURl.S3_BUCKET,
      Prefix : $scope.param.orderId+'/'+$scope.param.dateId.slice(0,10)+'/pop'
    }
    $scope.download_image(param)
  }

  $scope.downloadPod = function(){ 
    var param = {
      Bucket : baseURl.S3_BUCKET,
      Prefix : $scope.param.orderId+'/'+$scope.param.dateId.slice(0,10)+'/pod'
    }
    $scope.download_image(param)
  }

  var _safari = function(){
    var isSafari = /Safari/.test(navigator.userAgent) && /Apple Computer/.test(navigator.vendor);
    if(isSafari){
      var test_popup = window.open('')
      if(test_popup == null || typeof(test_popup) == undefined){
        return true;
      }
      else{
        return false;
      }
    }
    else{
      return false;
    }
  }

  $scope.download_image = function(param){
    var s3 = new AWS.S3()
    cfpLoadingBar.start();
    s3.listObjects(param, function (err, data){
      cfpLoadingBar.complete()
      if(err){
        alert(err)
      }
      else{
        if (data.Contents.length == 0) {
          $scope.notification.type = 'error'
          $scope.notification.message = "NO PROOF IMAGES WERE FOUND"
          $scope.$apply()
          $timeout(function(){
            $scope.hideNotificationBar()
          },5000)
          return;
        }
        if( _safari() ) {
          $scope.notification.type = 'warning'
          $scope.notification.message = 'To view the proofs! \nOption 1: Go to Safari —> Preferences —> Security —>  Block popup windows (Disable)\nOption 2: Use Chrome browser to download the images'
          $scope.$apply()
          $timeout(function(){
            $scope.hideNotificationBar()
          },7000)
          return;
        }
        else{
          data.Contents.forEach(function (img){
            s3.getObject({Bucket : baseURl.S3_BUCKET,Key: img.Key}, function (err, data){
              var base64string = btoa(String.fromCharCode.apply(null, data.Body))
              var image_proof = new Image()
              image_proof.src = "data:image/png;base64,"+base64string
              image_proof.onload = function(){
                var canvas = document.createElement('canvas');
                context = canvas.getContext('2d');
                context.canvas.width = this.width
                context.canvas.height = this.height
                context.drawImage(image_proof, 0,0);
                canvas.toBlob(function(blob) {
                  saveAs(blob, img.Key);
                },"image/png");
                delete canvas;
              }
            }); // end of s3 getObject
          }); // end of forEach
        } // end of else
      } // end of else 
    }) // end of listObject
  }

  $scope.deleteOrder = function(data){
    cfpLoadingBar.start();
    Orders.deleteOrder(data.id).finally(function(){
      var status = Errorhandler.getStatus()
      cfpLoadingBar.complete()
      if(status.has_error){
        $scope.notification.type = 'error'
        $scope.notification.message = status.error
        $timeout(function(){
          $scope.hideNotificationBar()
        },3000)
      }
      else{
        $scope.success_msg = 'Order Cancelled Successfully'
        $timeout(function(){
          $state.go('home.order',{date : $scope.param.dateId})
        },3000)
      }
    })
  }

  $scope.rescheduleOrder = function(reschedule_data){
    var dates = {
      old_date : $scope.param.dateId,
      new_date : reschedule_data.date
    }
    cfpLoadingBar.start();
    Orders.rescheduleOrder(reschedule_data.id,dates).finally(function(){
      var status = Errorhandler.getStatus()
      cfpLoadingBar.complete()
      if(status.has_error){
        $scope.notification.type = 'error'
        $scope.notification.message = status.error
        $timeout(function(){
          $scope.hideNotificationBar()
        },3000)
      }
      else{
        $scope.success_msg = 'Order rescheduled Successfully'
        $timeout(function(){
          $state.go('home.order',{date : $scope.param.dateId})
        },3000)
      }
    })
  }

  $scope.openDgModal =  function(order){
    var modalInstance =  $modal.open({
      templateUrl:'/static/webapp/partials/modals/dgAssignModal.html',
      controller:'modalDgCntrl',
      backdropClass : 'modal_back',
      windowClass :'modal_front',
      resolve : {
        details: function () {
          var object = {}
          // object.modal_scope = scope
          object.dgs = $scope.$parent.dgs
          object.pickupguy = order.pickupguy_id
          object.deliveryguy = order.deliveryguy_id
          return object;
        }
      }
    })

    modalInstance.result.then(function (data) {
      $scope.assign_dg(data,order.id)
    }, function () {
      console.log("Closed")
    });
  }

  $scope.assign_dg = function(dg_array,id){
    for(var i = dg_array.length -1; i >= 0 ; i--){
      if(dg_array[i].dg_id){
        dg_array[i].order_ids = [id],
        dg_array[i].date = $scope.param.dateId
      }
      else{
        dg_array.splice(i, 1);
      }
    }
    cfpLoadingBar.start();
    Orders.assignOrder(dg_array).then(function (data){
      cfpLoadingBar.complete();
      $scope.notification.type = 'success'
      $scope.notification.message = 'Orders assigned successfully'
      $timeout(function(){
        $scope.hideNotificationBar()
      },3000)
      $scope.getOrderById()
    },function (err){
      cfpLoadingBar.complete();
      $scope.notification.type = 'error'
      $scope.notification.message = status.error
      $timeout(function(){
        $scope.hideNotificationBar()
      },3000)
    })
  }
})

ygVendors.controller('dgCntrl',function ($scope,$state,DG,$filter,$stateParams,$location,$modal,filterFilter,Errorhandler,$interval,baseURl){
  $scope.datePicker = {}
  $scope.datePicker.date = ($stateParams.date!= undefined) ? new Date($stateParams.date) : new Date();
  $scope.datePicker.page = ($stateParams.page!= undefined) ? parseInt($stateParams.page): 1;
  $scope.datePicker.attendance = ($stateParams.attendance!= undefined) ? $stateParams.attendance : 'ALL';
  $scope.datePicker.search = $stateParams.search
  $scope.searched_id = $stateParams.search
  $scope.format = 'dd-MMM-yyyy'
  $scope.markers = []
  $scope.infowindow = new google.maps.InfoWindow();
  $scope.itemsByPage = baseURl.ItemByPage
  $scope.dgFilter = {}
  $scope.dgFilter.user = {}
  $scope.timeFilter = {
    today : new Date().setCustomHours(0),
    threeHour : new Date().subbActlHours(3),
    oneHour : new Date().subbActlHours(1)
  }

  $scope.attendance_status = ['ALL','ONLY_CHECKEDIN','NOT_CHECKEDIN','CHECKEDIN_AND_CHECKEDOUT']

  $scope.view = {
    list:true,
    map:false
  }
  
  $scope.getDg = function(){
    if($scope.datePicker.opened){
      delete $scope.datePicker.opened
    }
    $location.search($scope.datePicker)
    $scope.loaded = false;
    DG.getDgv2($scope.datePicker).finally(function(){
      $scope.loaded = true;
      var status = Errorhandler.getStatus()
      if(status.has_error){
        $scope.show_error_message = true
        $scope.error_msg = status.error
      }
      else{
        $scope.show_error_message = false
        $scope.dgs = status.data.data
        $scope.totalDgs = status.data.total_dg_count
      }
    })
  }

  $scope.diplay_dg = [].concat($scope.dgs)

  $scope.getDgv1 = function(){
    DG.getDgv1().finally(function(){
      $scope.loaded = true;
      var status = Errorhandler.getStatus()
      if(status.has_error){
        $scope.show_error_message = true
        $scope.error_msg = status.error
      }
      else{
        $scope.dgs_for_map = status.data
        $scope.filteredDg = filterFilter($scope.dgs_for_map,$scope.dgFilter.user.first_name)
        $scope.filteredDg = $filter('timeFilter')($scope.filteredDg,$scope.dgFilter.filter_time)
      }
    })
  }
  $scope.getDgv1()

  $scope.search_dg = function(id){
    if(id == undefined || id == ""){
      delete $scope.datePicker.search
      // $scope.datePicker.search = null
    }
    else{
      $scope.datePicker.search = id
    }
  }

  $scope.$watch('datePicker',function (newValue,oldValue){
    if(newValue){
      if(!angular.isString(oldValue.date)){
        oldValue.date = oldValue.date.toISOString()
      }
      if(!angular.isString(newValue.date)){
        newValue.date = newValue.date.toISOString()
      }
      if(newValue.search != oldValue.search){
        newValue.page = 1
      }
      else if(newValue.date != oldValue.date && newValue.search == oldValue.search || newValue.attendance!= oldValue.attendance && newValue.search == oldValue.search){
        newValue.page = 1
        newValue.search = undefined
        $scope.searched_id = null
      }
      $scope.getDg()
    }
  },true)

  $scope.$watchGroup(['dgFilter.user.first_name','dgFilter.filter_time'],function (newValue,oldValue,scope){
    if(scope.view.map){
      scope.filteredDg = filterFilter(scope.dgs_for_map,newValue[0])
      scope.filteredDg = $filter('timeFilter')(scope.filteredDg,newValue[1])
      scope.clearMarkers()
      scope.getDgsLatLng()
    }
  })

  $scope.getDgsLatLng = function(){
    $scope.markers = []
    $scope.dg_array = []
    var marker_image 
    for(var i =0; i<$scope.filteredDg.length;i++){
      if($scope.filteredDg[i].latitude!="" || $scope.filteredDg[i].longitude!=""){
        if($scope.filteredDg[i].status == "AVAILABLE" && $scope.filteredDg[i].transportation_mode == "WALKER"){
          marker_image = baseURl.MARKER_WALKER_AVAIL
        }
        else if($scope.filteredDg[i].status == "BUSY" && $scope.filteredDg[i].transportation_mode == "WALKER"){
          marker_image = baseURl.MARKER_WALKER_BUSY
        }
        else if($scope.filteredDg[i].status == "AVAILABLE" && $scope.filteredDg[i].transportation_mode == "BIKER"){
          marker_image = baseURl.MARKER_BIKER_AVAIL
        }
        else if($scope.filteredDg[i].status == "BUSY" && $scope.filteredDg[i].transportation_mode == "BIKER"){
          marker_image =  baseURl.MARKER_BIKER_BUSY
        }
        $scope.markers.push(
          new google.maps.Marker({
            position:new google.maps.LatLng(parseFloat($scope.filteredDg[i].latitude),parseFloat($scope.filteredDg[i].longitude)),
            map:$scope.map,
            icon : marker_image,
            info: "<b>"+$scope.filteredDg[i].user.first_name+"</b><br>"+$scope.filteredDg[i].user.username+
            "</b><br>"+ $filter('date')(new Date($scope.filteredDg[i].last_connected_time),'MMM dd yyyy - h:mma')
          })
        )
      }
    }
    for(var i=0;i<$scope.markers.length;i++){
      google.maps.event.addListener($scope.markers[i], 'mouseover', function () {
        $scope.infowindow.setContent(this.info);
        $scope.infowindow.open($scope.map, this);
      });
    }
  }

  $scope.clearMarkers = function () {
    for (var i = 0; i < $scope.markers.length; i++) {
      $scope.markers[i].setMap(null);
    }
    $scope.markers = [];
  }

  $scope.initialize_map = function(){
    $scope.mapOptions = {
      center: { lat: 19.072192, lng: 72.882577 },
      zoom: 11
    };
    $scope.map = new google.maps.Map(document.getElementById('map-canvas'),$scope.mapOptions);
    $scope.getDgsLatLng()
  }

  $interval(function(){
    if($scope.view.map){
      $scope.timeFilter = {
        today : new Date().setCustomHours(0),
        threeHour : new Date().subbActlHours(3),
        oneHour : new Date().subbActlHours(1)
      }
      $scope.getDgv1()
      $scope.clearMarkers()
      $scope.getDgsLatLng()
    }
  },10000)

  $scope.startopen = function($event) {
    $event.preventDefault();
    $event.stopPropagation();
    $scope.opened = true;
  }

  $scope.calculate_time_diff = function(inTime,outTime){
    inTime = new Date(inTime).getTime()
    outTime = new Date(outTime).getTime()
    var result = Math.round((outTime- inTime)/(60*60*1000));
    if(result >= 0){
      return result;
    }
    else{
      return 0;
    }
  }

  $scope.deleteDg = function(dg){
    $scope.loaded = false;
    DG.deleteDg(dg.id).finally(function(){
      var status = Errorhandler.getStatus()
      if(status.has_error){
        $scope.loaded = true;
        alert(status.error)
      }
      else{
        $scope.getDg()
      }
    })
  }

  $scope.deleteDgModal =  function(size,dg,e){
    e.stopPropagation()
    var modalInstance =  $modal.open({
      templateUrl:'/static/webapp/partials/modals/confirmModal.html',
      controller:'modalConfirmCntrl',
      size :size,
      backdropClass : 'modal_back',
      windowClass :'modal_front',
      resolve : {
        details: function () {
          var object = {}
          object.modal_scope = 'delete_customer'
          object.message = "You want to delete delivery boy"
          object.action_on = dg
          return object;
        }
      }
    })

    modalInstance.result.then(function (dg) {
      $scope.deleteDg(dg)
    }, function () {
      console.log("Closed")
    });
  }
})

ygVendors.controller('createDgCntrl' ,function ($scope,$state,DG,Errorhandler,$timeout,baseURl){
  $scope.dg = {}
  $scope.dg.role = baseURl.ROLE.dg

  $scope.createDg = function(){
    $scope.dg_in_process = true
    DG.createDg($scope.dg).finally( function(){
      var status = Errorhandler.getStatus()
      $scope.dg_in_process = false
      if(status.has_error){
        $scope.show_alert_message = true
        $scope.alert_message = status.error
      }
      else{
        $scope.success_msg =true
        $timeout(function(){
          $state.go('home.dg')
        },3000)
      }
    })
  }
})

ygVendors.controller('dgDetailsCntrl', function ($scope,$stateParams,DG,Errorhandler){
  $scope.tabs = {}
  $scope.tabs.details = true;
  $scope.format = 'MMMM-yyyy'
  $scope.opened = false;
  $scope.date = new Date();
  $scope.dgId = $stateParams.dgId
  $scope.days = new Array(31)

  $scope.getDgById = function(){
    $scope.detailLoading = true
    DG.getDgById($scope.dgId).finally(function(){
      var status = Errorhandler.getStatus()
      $scope.detailLoading = false
      if(status.has_error){
        alert(status.error)
      }
      else{
        $scope.dg_detail = status.data
      }
    })
  }
   $scope.getDgById();

  $scope.startopen = function($event) {
    $event.preventDefault();
    $event.stopPropagation();
    $scope.opened = true;
  };

  $scope.getAttendanceById = function(month,year){
    var dg_attendance = {
      month : month,
      year : year
    }
    $scope.attendance_loaded = false;
    DG.getAttendanceById($scope.dgId,dg_attendance).finally(function(){
      var status = Errorhandler.getStatus()
      $scope.attendance_loaded = true;
      if(status.has_error){
        alert(status.error)
      }
      else{
        var days_length = new Date(year, month,0).getDate();
        $scope.days = new Array(days_length);
        for(i=0;i<status.data.length;i++){
          var day = new Date(status.data[i].date).getDate()
          $scope.days[day -1] = status.data[i]
        }
      }
    })
  }

  $scope.display_days = [].concat($scope.days);


  $scope.$watch('date', function (newValue,oldValue,scope){
    if(newValue){
      scope.getAttendanceById(newValue.getMonth()+1,newValue.getFullYear())
    }
  })

  $scope.calculate_time_diff = function(inTime,outTime){
    inTime = new Date(inTime).getTime()
    outTime = new Date(outTime).getTime()
    var result = Math.round((outTime- inTime)/(60*60*1000));
    if(result >= 0){
      return result;
    }
    else{
      return '---';
    }
  }

  $scope.setDate = function(day){
    var x = new Date($scope.date)
    x.setDate(day)
    return x;
  }
})

ygVendors.controller('vendorCntrl', function ($scope,Vendors,Errorhandler,baseURl){
  $scope.itemsByPage = baseURl.ItemByPage

  $scope.getVendor =  function(){
    $scope.VendorLoading = true
    Vendors.getVendor().then(function (response){
      $scope.VendorLoading = false
      $scope.vendors = response.data.data
    }, function (response){
      $scope.VendorLoading = false
    })
  }

  $scope.getRequestedVendors = function(){
    $scope.rqstVendorLoading = true
    Vendors.getRequestedVendor().finally(function(){
      var status = Errorhandler.getStatus()
      $scope.rqstVendorLoading = false
      if(status.has_error){
        // console.log(status.error)
      }
      else{
        $scope.requestedVendors = status.data.data
      }
    })
  }

  $scope.display_vendor = [].concat($scope.vendors)
  $scope.display_rqst_vendor = [].concat($scope.requestedVendors)
})

ygVendors.controller('vendorDetailsCntrl', function ($scope,$stateParams,$timeout,$state,Vendors,Errorhandler){
  $scope.vendor = $stateParams.vendorId
  $scope.editable = false
  $scope.getVendorById = function(){
    $scope.detailLoading = true
    Vendors.getVendorById($scope.vendor).finally(function(){
      var status = Errorhandler.getStatus()
      $scope.detailLoading = false
      if(status.has_error){
        alert(status.error)
      }
      else{
        $scope.vendor_detail = status.data.data
      }
    })
  }

  $scope.getVendorById()

  $scope.approve_vendor = function(){
    $scope.approve_in_process = true;
    var note = {
      notes: $scope.vendor_detail.notes
      ,is_retail : $scope.vendor_detail.is_retail
    }
    // console.log(note)
    Vendors.approveById($scope.vendor,note).finally(function(){
      var status = Errorhandler.getStatus()
      $scope.approve_in_process = false;
      if(status.has_error){
        alert(status.error)
      }
      else{
        $scope.success_msg = true;
        $timeout(function(){
          $state.go('home.vendor')
        },3000)
      }
    })
  }
})

ygVendors.controller('customerDetailsCntrl',function ($scope,$stateParams,$timeout,$modal,Consumers,StoreSession,Errorhandler){
  $scope.user = $stateParams.customerId
  $scope.editable = false
  $scope.getUserById = function(){
    $scope.detailLoading = true
    Consumers.getConsumerById($scope.user).finally(function(){
      var status = Errorhandler.getStatus()
      $scope.detailLoading = false
      if(status.has_error){
        alert(status.error)
      }
      else{
        $scope.user_detail = status.data.data
        $scope.user_detail.address_id = $scope.user_detail.addresses[0].id
        StoreSession.updateCustomer($scope.user_detail)
      }
    })
  }

  $scope.getUserById()

  $scope.addAddress = function(address){
    $scope.detailLoading = true
    Consumers.addAddress($scope.user,address).finally(function(){
      var status = Errorhandler.getStatus()
      if(status.has_error){
        $scope.detailLoading = false
        alert(status.error)
      }
      else{
        $scope.getUserById()
      }
    })
  }

  $scope.openAddressModal =  function(){
    var modalInstance =  $modal.open({
      templateUrl:'/static/webapp/partials/modals/addAddress.html',
      controller:'addAddressPopup',
      backdropClass : 'modal_back',
      windowClass :'modal_front',
      resolve : {
        details: function () {
          var object = {}
          object.area_codes = $scope.$parent.area_codes
          return object;
        }
      }
    })

    modalInstance.result.then(function (data) {
      $scope.addAddress(data)
    }, function () {
      console.log("Closed")
    });
  }

  $scope.deleteAddress = function(address_id){
    $scope.detailLoading = true
    Consumers.deleteAddress($scope.user,{address_id:address_id}).finally(function(){
      var status = Errorhandler.getStatus()
      if(status.has_error){
        $scope.detailLoading = false
        alert(status.error)
      }
      else{
        $scope.getUserById()
      }
    })
  }

  $scope.openModal =  function(address_id){
    var modalInstance =  $modal.open({
      templateUrl:'/static/webapp/partials/modals/confirmModal.html',
      controller:'modalConfirmCntrl',
      backdropClass : 'modal_back',
      windowClass :'modal_front',
      resolve : {
        details: function () {
          var object = {}
          object.modal_scope = 'delete_address'
          object.message = "You want to delete this address"
          object.action_on = address_id
          return object;
        }
      }
    })

    modalInstance.result.then(function (address_id) {
      $scope.deleteAddress(address_id)
    }, function () {
      console.log("Closed")
    });
  }
}) 

ygVendors.controller('accountSettingCntrl', function ($scope,$modal,Vendors,Errorhandler){

  $scope.addAddress = function(address){
    $scope.detailLoading = true
    Vendors.addAddress($scope.user.id,address).finally(function(){
      var status = Errorhandler.getStatus()
      if(status.has_error){
        alert(status.error)
      }
      else{
        $scope.getUsername()
      }
    })
  }

  $scope.openAddressModal =  function(){
    var modalInstance =  $modal.open({
      templateUrl:'/static/webapp/partials/modals/addAddress.html',
      controller:'addAddressPopup',
      backdropClass : 'modal_back',
      windowClass :'modal_front',
      resolve : {
        details: function () {
          var object = {}
          object.area_codes = $scope.area_codes
          return object;
        }
      }
    })

    modalInstance.result.then(function (data) {
      $scope.addAddress(data)
    }, function () {
      console.log("Closed")
    });
  }

  $scope.deleteAddress = function(address_id){
    Vendors.deleteAddress($scope.user.id,{address_id:address_id}).finally(function(){
      var status = Errorhandler.getStatus()
      if(status.has_error){
        alert(status.error)
      }
      else{
        $scope.getUsername()
      }
    })
  }

  $scope.openModal =  function(address_id){
    var modalInstance =  $modal.open({
      templateUrl:'/static/webapp/partials/modals/confirmModal.html',
      controller:'modalConfirmCntrl',
      backdropClass : 'modal_back',
      windowClass :'modal_front',
      resolve : {
        details: function () {
          var object = {}
          object.modal_scope = 'delete_address'
          object.message = "You want to delete this address"
          object.action_on = address_id
          return object;
        }
      }
    })

    modalInstance.result.then(function (address_id) {
      $scope.deleteAddress(address_id)
    }, function () {
      console.log("Closed")
    });
  }
})

ygVendors.controller('fileUploadCntrl' ,function ($scope,$filter,$timeout,$state,Orders,cfpLoadingBar,Errorhandler){
  $scope.select_pickup = function(id){
    $scope.pickup_address = id
  }

  $scope.showContent = function($fileContent){
    $scope.content = $fileContent;
  };

  var checkEmptyObject = function(data){
    var flag = true;
    for(var key in data){
      if(!(/^\s*$/.test(data[key]))) {
        flag =  false;
      }
    }
    return flag;
  };

  $scope.UploadFile = function(){
    $scope.upload_data = {}
    var vendor_id_set = new Set();
    for(i = $scope.content.length-1; i >= 0; i-- ){
      if(checkEmptyObject($scope.content[i])){
        $scope.content.splice(i, 1);
      }
      else{
        if(!$scope.content[i].hasOwnProperty('date')){
          alert('Date not present for customer '+$scope.content[i].customer_name+' at line '+(i+1))
          return false;
        }
        else if(!$scope.content[i].hasOwnProperty('vendor_order_id')){
          alert('Vendor Order Id not present for customer '+$scope.content[i].customer_name+' at line '+(i+1))
          return false;
        }
        else if(!$scope.content[i].hasOwnProperty('pickup_time')){
          alert('Pickup Time not present for customer '+$scope.content[i].customer_name+' at line '+(i+1))
          return false;
        }
        else if(!$scope.content[i].hasOwnProperty('customer_name')){
          alert('Customer Name not present for customer '+$scope.content[i].customer_name+' at line '+(i+1))
          return false;
        }
        else if(!$scope.content[i].hasOwnProperty('customer_phone_number')){
          alert('Customer Phone Number not present for customer '+$scope.content[i].customer_name+' at line '+(i+1))
          return false;
        }
        else if(!$scope.content[i].hasOwnProperty('delivery_full_address')){
          alert('Delivery Street not present for customer '+$scope.content[i].customer_name+' at line '+(i+1))
          return false;
        }
        else if(!$scope.content[i].hasOwnProperty('delivery_pincode')){
          alert('Delivery Pincode not present for customer '+$scope.content[i].customer_name+' at line '+(i+1))
          return false;
        }
        else{
          vendor_id_set.add($scope.content[i].vendor_order_id)
          var time = $scope.content[i].pickup_time.split(':')
          var datetime = new Date($scope.content[i].date)
          datetime.setHours(parseInt(time[0]))
          datetime.setMinutes(parseInt(time[1]))
          $scope.content[i].pickup_datetime = datetime.toISOString()
          delete $scope.content[i].pickup_time
          delete $scope.content[i].date
        }
      }
    }
    if(vendor_id_set.size != $scope.content.length){
      alert('Duplicate vendor order Id are present')
      return
    }
    else{
      $scope.upload_data.pickup_address_id = $scope.pickup_address 
      $scope.upload_data.orders = $scope.content
      cfpLoadingBar.start()
      Orders.fileUpload($scope.upload_data).finally(function(){
        var status = Errorhandler.getStatus()
        cfpLoadingBar.complete()
        $('#fileUpload').val('')
        $scope.in_process = false
        if(status.has_error){
          alert(status.error)
        }
        else{
          $scope.show_success_msg = true;
          $scope.success_msg = "File uploaded successfully"
          $timeout(function(){
            $state.go('home.order')
          },3000)
        }
      })
    }
  }
})

ygVendors.controller('reportsCntrl', function ($scope,$timeout,Dashboard,Errorhandler,cfpLoadingBar){
  $scope.format = 'dd-MMM-yyyy';
  $scope.dash_data = {
    start_date : new Date(),
    end_date : new Date()
  };
  $scope.dash_data.start_date.setDate(1)
  $scope.notification = {};
  $scope.datePicker = {}
  $scope.graphData = {}
  $scope.graphData.chart = {
    plotGradientColor : " ",
    plotSpacePercent : "60",
    caption: "Order Details",
    xaxisname: "Dates",
    yaxisname: "Orders",
    showalternatehgridcolor: "0",
    placevaluesinside: "1",
    toolTipSepChar : '=',
    showborder: "0",
    showvalues: "0",
    showplotborder: "0",
    showcanvasborder: "0",
    theme: "fint"
  }
  $scope.graphData.categories = [
    {
      category: []
    }
  ]
  $scope.graphData.dataset = [
    {
      seriesname: "Total Delivered",
      color: "39B54A",
      data:[]
    },
    {
      seriesname: "Total Attempted",
      color: "00CCFF",
      data:[]
    },
    {
      seriesname: "Total Intransit",
      color: "FCC06A",
      data:[]
    },
    {
      seriesname: "Total Queued",
      color: "FE5E64",
      data:[]
    },
    {
      seriesname: "Total Cancelled",
      color: "A6A6A6",
      data:[]
    },
  ]

  $scope.open = function($event,which) {
    $event.preventDefault();
    $event.stopPropagation();
    $scope.datePicker[which] = true;
  }

  $scope.hideNotificationBar = function(){
    $scope.notification.type = null
    $scope.notification.message = null
  }

  $scope.error_handler = function(type,message){
    $scope.notification.type = type
    $scope.notification.message = message
    $timeout(function(){
      $scope.hideNotificationBar()
    },5000)
  }

  $scope.$watch('dash_data', function (newValue,oldValue,scope){
    if(newValue){
      cfpLoadingBar.start();
      if(newValue.end_date < newValue.start_date){
        newValue.end_date = newValue.start_date
      }
      Dashboard.getData(newValue).finally(function(){
        var status = Errorhandler.getStatus()
        cfpLoadingBar.complete()
        if(status.has_error){
          $scope.error_handler('error',status.error)
        }
        else{
          scope.dashboard_value = status.data
          if( scope.dashboard_value.total_orders == 0) {
            scope.no_reports_msg = 'Hello ! There are no reports yet, please place orders to view your reports.'
          }
          else{
            scope.no_reports_msg = undefined;
            scope.graphData.categories[0].category = []
            scope.graphData.dataset[0].data = []
            scope.graphData.dataset[1].data = []
            scope.graphData.dataset[2].data = []
            scope.graphData.dataset[3].data = []
            scope.graphData.dataset[4].data = []
            for(var i=0; i < scope.dashboard_value.orders.length;i++){
              scope.graphData.categories[0].category[i] = {}
              scope.graphData.categories[0].category[i].label = scope.dashboard_value.orders[i].date.slice(8,10)
              scope.graphData.dataset[0].data[i] = {}
              scope.graphData.dataset[1].data[i] = {}
              scope.graphData.dataset[2].data[i] = {}
              scope.graphData.dataset[3].data[i] = {}
              scope.graphData.dataset[4].data[i] = {}
              scope.graphData.dataset[0].data[i].value = scope.dashboard_value.orders[i].delivered_count   
              scope.graphData.dataset[0].data[i].toolText = "Total Delivered:"+scope.dashboard_value.orders[i].delivered_count+"{br} Total Placed:"+scope.dashboard_value.orders[i].total_orders_count+"{br}"+new Date(scope.dashboard_value.orders[i].date).toDateString()
              scope.graphData.dataset[1].data[i].value = scope.dashboard_value.orders[i].delivery_attempted_count+scope.dashboard_value.orders[i].pickup_attempted_count  
              scope.graphData.dataset[1].data[i].toolText = "Total Attempted:"+(scope.dashboard_value.orders[i].delivery_attempted_count+scope.dashboard_value.orders[i].pickup_attempted_count)+"{br} Total Placed:"+scope.dashboard_value.orders[i].total_orders_count+"{br}"+new Date(scope.dashboard_value.orders[i].date).toDateString()
              scope.graphData.dataset[2].data[i].value = scope.dashboard_value.orders[i].intransit_count   
              scope.graphData.dataset[2].data[i].toolText = "Total Intransit:"+scope.dashboard_value.orders[i].intransit_count+"{br} Total Placed:"+scope.dashboard_value.orders[i].total_orders_count+"{br}"+new Date(scope.dashboard_value.orders[i].date).toDateString()
              scope.graphData.dataset[3].data[i].value = scope.dashboard_value.orders[i].queued_count   
              scope.graphData.dataset[3].data[i].toolText = "Total Queued:"+scope.dashboard_value.orders[i].queued_count+"{br} Total Placed:"+scope.dashboard_value.orders[i].total_orders_count+"{br}"+new Date(scope.dashboard_value.orders[i].date).toDateString()
              scope.graphData.dataset[4].data[i].value = scope.dashboard_value.orders[i].cancelled_count   
              scope.graphData.dataset[4].data[i].toolText = "Total Cancelled:"+scope.dashboard_value.orders[i].cancelled_count+"{br} Total Placed:"+scope.dashboard_value.orders[i].total_orders_count+"{br}"+new Date(scope.dashboard_value.orders[i].date).toDateString()
            }
          }
        }
      })
    }
  },true)

  var excelStyle = {
    sheetid:"Sheet name",
    headers:true,
    column: {
      style:{ 'font-size':'10px','width':'200px'}
    }
  }
  
  $scope.downloadExcelData = function(){
    cfpLoadingBar.start()
    Dashboard.getExcelData($scope.dash_data).finally(function(){
      var excel_status = Errorhandler.getStatus()
      cfpLoadingBar.complete()
      if(excel_status.has_error){
        $scope.error_handler('error',excel_status.error)
      }
      else{
        $scope.excel_data = excel_status.data.orders
        var slect_string = '*'
        if($scope.$parent.role.ops){
          slect_string = 'date,order_id,customer_name,customer_phone_number,cod_amount,cod_collected,cod_reason,status,delivery_guy,vendor_name,vendor_order_id,vendor_notes'
        }
        else{
          slect_string = 'date,order_id,customer_name,customer_phone_number,cod_amount,cod_collected,cod_reason,status,vendor_order_id,vendor_notes'
        }
        alasql('SELECT '+slect_string+' INTO XLSX("orders.xlsx",?) FROM ?',[excelStyle,$scope.excel_data]);
      }  
    })
  }
})

ygVendors.controller('complaintsCntrl' , function ($scope,Complaints,StoreSessionData,Errorhandler,cfpLoadingBar){
  $scope.getTicketAndGroup = function(){
    if(StoreSessionData.getData('ticket_gruops')){
      cfpLoadingBar.start();
      Complaints.getTickets().finally(function(){
        var status =  Errorhandler.getStatus()
        if(status.has_error){
          cfpLoadingBar.complete()
          $scope.show_complaint_msg = true;
          $scope.complaint_msg = status.error;
        }
        else{
          cfpLoadingBar.complete()
          $scope.groups = StoreSessionData.getData('ticket_gruops')
          if(status.data.errors || status.data.length == 0){
            $scope.show_complaint_msg = true;
            $scope.complaint_msg = 'Happy to Help!';
          }
          else{
            $scope.show_complaint_msg = false;
            $scope.complaints = status.data
          }
        }
      })
    }
    else{
      cfpLoadingBar.start();
      Complaints.getTicketAndGroup().then(function (data){
        cfpLoadingBar.complete();
        $scope.groups = data.groups;
        StoreSessionData.setData('ticket_gruops',$scope.groups);
        if(data.tickets.errors || data.tickets.length == 0 ){
            $scope.show_complaint_msg = true;
            $scope.complaint_msg = 'Happy to Help!';
        }
        else{
          $scope.show_complaint_msg = false;
          $scope.complaints = data.tickets
        }
      },function (err){
        cfpLoadingBar.complete()
        $scope.show_complaint_msg = true;
        $scope.complaint_msg = err;
      })
    }
  }

  $scope.display_complaints = [].concat($scope.complaints)

  $scope.getGroupName = function(id){
    return StoreSessionData.returnGruopName(id)
  }

  $scope.getTicketAndGroup()
})

ygVendors.controller('createComplaintsCntrl',function ($scope,$timeout,$state,StoreSessionData,Complaints,cfpLoadingBar,Errorhandler){
  $scope.priorities = {
    "Low":1,
    "Medium":2,
    "High":3,
    "Urgent":4
  }

  $scope.complain_status = {
    "Open":2,
    "Pending":3,
    "Resolved":4,
    "Closed":5
  }

  $scope.getGroups = function(){
    if(StoreSessionData.getData('ticket_gruops')){
      $scope.groups = StoreSessionData.getData('ticket_gruops')
    }
    else{
      cfpLoadingBar.start();
      Complaints.getGroups().finally(function(){
        var status =  Errorhandler.getStatus()
        if(status.has_error){
          cfpLoadingBar.complete()
          alert(status.error)
        }
        else{
          cfpLoadingBar.complete()
          $scope.groups = status.data
          StoreSessionData.setData('ticket_gruops',$scope.groups)
        }
      })
    }
  }

  $scope.getGroups()

  $scope.doComplain = function(){
    cfpLoadingBar.start();
    $scope.complain_btn_disable = true
    Complaints.creatTickets($scope.tickets).finally(function(){
      var status =  Errorhandler.getStatus()
      if(status.has_error){
        cfpLoadingBar.complete()
        alert(status.error)
        $scope.complain_btn_disable = false
      }
      else{
        cfpLoadingBar.complete()
        $scope.show_success_msg =true
        $scope.success_msg = "Feedback submitted successfully"
        $timeout(function(){
          $state.go('home.complaints')
        },3000)
      }

    })
  }
})

ygVendors.controller('detailComplaintsCntrl', function ($scope,$stateParams,StoreSessionData,Complaints,cfpLoadingBar,Errorhandler){
  var ticket_id =  $stateParams.id

  $scope.getTicket = function(id){
    if(StoreSessionData.getData('ticket_gruops')){
      cfpLoadingBar.start();
      Complaints.getTicketById(id).finally(function(){
        var status = Errorhandler.getStatus()
        if(status.has_error){
          cfpLoadingBar.complete()
          alert(status.error)
        }
        else{
          cfpLoadingBar.complete()
          $scope.ticket = status.data
        }
      })
    }
    else{
      cfpLoadingBar.start();
      Complaints.getTicketByIdAndGroup(id).then(function(data){
        cfpLoadingBar.complete()
        $scope.ticket = data.ticket_with_id
        StoreSessionData.setData('ticket_gruops',data.groups)
      },function (err){
        cfpLoadingBar.complete()
        alert(err)
      })
    }
  }

  $scope.getTicket(ticket_id)

  $scope.addNotes = function(){
    $scope.show_note_section = true;
    $scope.submit_notes = true;
  }

  $scope.resolveComplain = function(){
    $scope.show_note_section = true;
    $scope.submit_resolve = true;
  }

  $scope.hideNotes = function(){
    $scope.show_note_section = false;
    $scope.submit_resolve = false;
    $scope.submit_notes = false;
  }

  $scope.getUsername =  function(id){
    if(id == $scope.ticket.helpdesk_ticket.requester_id){
      return $scope.ticket.helpdesk_ticket.requester_name;
    }
    else{
      return $scope.ticket.helpdesk_ticket.responder_name;
    }
  }

  $scope.getGroupName = function(id){
    return StoreSessionData.returnGruopName(id)
  }

  $scope.submitNote = function(data){
    data.id = ticket_id
    if($scope.$parent.role.ops){
      data.note.helpdesk_note.user_id = $scope.ticket.helpdesk_ticket.responder_id
    }
    else{
      data.note.helpdesk_note.user_id = $scope.ticket.helpdesk_ticket.requester_id
    }
    cfpLoadingBar.start();
    Complaints.addNotes(data).finally(function(){
      var status = Errorhandler.getStatus()
      if(status.has_error){
        cfpLoadingBar.complete()
        alert(status.error)
      }
      else{
        cfpLoadingBar.complete()
        $scope.show_note_section = false;
        $scope.submit_notes = false;
        $scope.getTicket(ticket_id)
      }
    })
  }

  $scope.closeComplain = function(data){
    data.id = ticket_id
    if($scope.$parent.role.ops){
      data.note.helpdesk_note.user_id = $scope.ticket.helpdesk_ticket.responder_id
    }
    else{
      data.note.helpdesk_note.user_id = $scope.ticket.helpdesk_ticket.requester_id
    }
    data.resolve = {
      helpdesk_ticket :{
        status: "5"
      }
    }
    cfpLoadingBar.start();
    Complaints.closeComplain(data).finally(function(){
      var status = Errorhandler.getStatus()
      if(status.has_error){
        cfpLoadingBar.complete()
        alert(status.error)
      }
      else{
        cfpLoadingBar.complete()
        $scope.show_note_section = false;
        $scope.submit_resolve = false;
        $scope.getTicket(ticket_id)
      }
    })
  }
})

ygVendors.controller('tutorialCntrl',function ($scope,$stateParams){
  $scope.myInterval = 0;
  $scope.noWrapSlides = true;
  var slides = $scope.slides = []

  $scope.addSlide = function() {
    var newWidth = slides.length + 1;
     slides.push({
      image: '/static/webapp/images/tutorial/' + newWidth + '.jpg',
      text: ['Check Your Orders','Create Orders','Add Your Customers','Get All Your Reports', 'Provide Your Feedback'][slides.length % 5]
    });
  };

  for (var i=0; i<5; i++) {
    $scope.addSlide();
  }
})


//Modal Controllers start from here................................................

ygVendors.controller('modalConfirmCntrl', function ($scope,$modalInstance,details){
  $scope.scope_details = {
    Logout: 'logout',
    Delete_Cust : 'delete_customer',
    Approve_order : 'approve_order',
    Decline_order : 'decline_order',
    Delete_order : 'delete_order',
    Delete_Address : 'delete_address',
    Reschedule_order : 'reschedule_order'
  }
  $scope.minDate = new Date()
  $scope.reschedule_date = new Date()
  $scope.reschedule_date.setHours(6)
  $scope.selectedDates = []

  $scope.details = details
  $scope.ok = function(){
    $modalInstance.close($scope.details.action_on)
  }

  $scope.approve_order = function(id){
    var data = {
      status : 'approve',
      id:id,
      message : null
    }
    $modalInstance.close(data)
  }

  $scope.decline_order = function(id){
    var data = {
      status : 'reject',
      id:id,
      message : $scope.reject_message
    }
    $modalInstance.close(data)
  }

  $scope.delete_order = function(order){
    var data = {
      status : 'delete',
      order:order
    }
    $modalInstance.close(data)
  }

  $scope.reschedule_order = function(data){
    data.status = 'reschedule'
    data.date = data.date.toISOString()
    $modalInstance.close(data)
  }

  $scope.cancel = function(){
    $modalInstance.dismiss('cancel');
  }
})

ygVendors.controller('orderStatusCntrl', function ($scope,$modalInstance,details){
  $scope.details = details;
  $scope.status = {}
  $scope.status.order_to_update = []

  for(var i = 0; i< details.order_ids.length;i++){
    $scope.status.order_to_update[i] = {}
    $scope.status.order_to_update[i].id = details.order_ids[i]
  }

  $scope.delivered_place = ['CUSTOMER','RECEPTION','DOOR_STEP','SECURITY']

  $scope.change_status = function(status){
    $modalInstance.close(status)
  }

  $scope.select_status = function(status_value){
    $scope.status.name = status_value;
  }

  $scope.select_place = function(place){
    $scope.status.delivered_at = place;
  }

  $scope.cancel = function(){
    $modalInstance.dismiss('cancel');
  }
})

ygVendors.controller('modalDgCntrl' , function ($scope,$modalInstance,details){
  $scope.details = details;
  $scope.dg_assign_array = [
    {dg_id:$scope.details.pickupguy,assignment_type:'pickup'},
    {dg_id:$scope.details.deliveryguy,assignment_type:'delivery'}
  ]

  $scope.setDefaultDg = function(dg,object){
    if(dg.id == object.dg_id){
      if(object.assignment_type == 'pickup'){
        $scope.dg_assign_array[0].dg_name = dg.user.first_name
      }
      else{
        $scope.dg_assign_array[1].dg_name = dg.user.first_name
      }
    }
  }

  $scope.assign_dg = function(){
    if($scope.dg_assign_array[0].dg_id && $scope.dg_assign_array[0].dg_id == $scope.details.pickupguy){
      $scope.dg_assign_array[0].dg_id = undefined
    }
    if($scope.dg_assign_array[1].dg_id && $scope.dg_assign_array[1].dg_id == $scope.details.deliveryguy){
      $scope.dg_assign_array[1].dg_id = undefined
    }
    $modalInstance.close($scope.dg_assign_array)
  }

  $scope.cancel = function(){
    $modalInstance.dismiss('cancel');
  }
})

ygVendors.controller('addAddressPopup', function ($scope,$modalInstance,details){
  $scope.details = details;

  $scope.addAddress = function(){
    $modalInstance.close($scope.address)
  } 

  $scope.cancel = function(){
    $modalInstance.dismiss('cancel');
  }
})

ygVendors.controller('addProductPopup', function ($scope,$modalInstance,details,Products,Errorhandler){
  $scope.product = {}
  $scope.product.vendor = details.user.id
  $scope.error_msg = undefined
  $scope.product_in_process = false
  $scope.show_error_message = false
  
  $scope.createProduct = function(){
    $scope.product_in_process = true
    $scope.error_msg = undefined
    Products.createProduct($scope.product).finally(function(){
      var status = Errorhandler.getStatus()
      $scope.product_in_process = false
      if(status.has_error){
        $scope.error_msg = status.error
      }
      else{
        $modalInstance.close(status.data)
      }
    })
  }

  $scope.cancelPopup = function(){
    $modalInstance.dismiss();
  }
})

ygVendors.controller('addCustomerPopup', function ($scope,$modalInstance,details,Consumers,Errorhandler){
  $scope.customer = {}
  $scope.cust_in_process = false
  $scope.error_msg = undefined
  $scope.area_codes = details.area_codes

  $scope.createCustomer = function(){
    $scope.cust_in_process = true
    $scope.error_msg = undefined
    Consumers.create($scope.customer).finally(function(){
      var status = Errorhandler.getStatus()
      $scope.cust_in_process = false
      if(status.has_error){
        $scope.error_msg = status.error
      }
      else{
        $scope.customer.addresses = [{
          pin_code : $scope.customer.pin_code,
          full_address : $scope.customer.full_address,
          id: status.data.new_address_id
        }]
        $scope.customer.address_id = $scope.customer.addresses[0].id
        $scope.customer.id = status.data.consumer_id
        delete $scope.customer.full_address
        delete $scope.customer.full_address
        $modalInstance.close($scope.customer)
      }
    })
  }

  $scope.cancelPopup = function(){
    $modalInstance.dismiss();
  }
})