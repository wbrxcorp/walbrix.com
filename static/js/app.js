angular.module('MyApp', ['ngResource', 'angulartics', 'angulartics.google.analytics','angulartics.scroll','angular-loading-bar','ui.bootstrap'])
.config(["$analyticsProvider", function($analyticsProvider) {
    //$analyticsProvider.vistualPageViews(false);
}])
.controller("Quote", ["$scope", "$resource", "$filter", function($scope, $resource, $filter) {
    var price_data = $resource($scope.root_path + "/product/stdserver/:name.json");
    var number_filter = $filter('number');
    
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

    $scope.option_label = function(name, price) {
        if (price > 0) {
            return name + " +" + number_filter(price, 0) + "円";
        } else {
            return name;
        }
    }

    $scope.apply_coupon = function() {
        load("_" + $scope.coupon_code.toLowerCase());
    }

    $scope.total = function() {
    if (!$scope.price_data) return undefined;
        return $scope.price_data.base_price + $scope.cpu.price + $scope.ram.price + $scope.hdd.price;
    }

    $scope.support_fee = function() {
        return 10000;
    }

    load("default");

}])
.controller("Inquiry", ["$scope", "$resource", "$modal", function($scope, $resource, $modal) {
    var inquiry = $resource($scope.root_path + "/inquiry");
    $scope.inquiry = {};
    $scope.submit = function(success_modal) {
        var modalInstance = $modal.open({
            templateUrl: $scope.root_path + "/static/progress.html", 
            backdrop:"static",keyboard:false
        });
        inquiry.save($scope.inquiry, function() {
            modalInstance.close();
            $scope.inquiry = {};
            if (!success_modal) success_modal = $scope.root_path + "/static/inquiry_success.html";
            $modal.open({templateUrl: success_modal});
        }, function() {
            modalInstance.close();
            $modal.open({templateUrl: $scope.root_path + "/static/error.html"});
        });
    }
}])
.run([ "$rootScope", "$location", "$analytics", "$modal", function($scope, $location, $analytics, $modal) {
    $scope.tax_rate = 1.08;
    $scope.root_path = (window["ROOT_PATH"] || "/").replace(/\/*$/, "");
    $scope.modal = function(template) {
        $modal.open({
            templateUrl: template
        });
    }
}]);
