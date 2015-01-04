angular.module('MyApp', ['ngResource', 'angulartics', 'angulartics.google.analytics','angulartics.scroll','angular-loading-bar'])
.config(["$analyticsProvider", function($analyticsProvider) {
    //$analyticsProvider.vistualPageViews(false);
}])
.controller("Quote", ["$scope", "$resource", function($scope, $resource) {
    var price_data = $resource("./:name.json");
    
    function load(name) {
	price_data.get({name:name, t:new Date().getTime()}, function(price_data) {
	    $scope.cpu = price_data.CPU[0];
	    $scope.ram = price_data.RAM[0];
	    $scope.hdd = price_data.HDD[0];
	    $scope.price_data = price_data;
	    $scope.error = null;
	}, function() {
	    $scope.error = "クーポンコードが正しくありません";
	});
    }

    $scope.apply_coupon = function() {
	load("_" + $scope.coupon_code.toLowerCase());
    }

    load("default");

}])
.run([ "$rootScope", "$location", "$analytics", function($scope, $location, $analytics) {
    //$analytics.pageTrack($location.path());
}]);
