angular.module('ClassieApp', [])

.controller('AppCtrl', ['$scope', '$log', '$http', function($scope, $log, $http) {
    $scope.courses = [];
    /* $http.get("/data").success(function(data) { 
	    $scope.data = data;
        console.log($scope.data);
    });
    */
    $http.get("/courses").success(function(data) {
        $scope.courses = data['data'];
        addAutocomplete();
    });
    $scope.search = function() {
        // do something
        console.log("submitted");
    }
}]);
