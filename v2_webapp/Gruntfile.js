module.exports = function(grunt){
	grunt.initConfig({
		pkg: grunt.file.readJSON('package.json'),
		bower_concat: {
			all: {
				dest: 'static/assets/js/vendors.js',
				exclude: [
					'angular-material-sass-files'
				],
				dependencies: {
					'alasql': ['jszip','js-xlsx','js-xls','es6-promise'],
					'fusioncharts' : ['ngstorage']
				},
				mainFiles : {
					fusioncharts : ['fusioncharts.js','fusioncharts.charts.js','angular-fusioncharts.min.js']
				}
			}
		},
		shell: {
			bowerinstall: {
				command: function(libname){
					return 'bower install ' + libname + ' -S';
				}
			},
			bowerupdate: {
				command: function(libname){
					return 'bower update ' + libname + ' -S';
				}
			}
		},
		uglify: {
			bower: {
				options: {
					mangle: true,
					compress: true,
					preserveComments: false,
					sourceMap: true,
					banner:  '/*! <%= pkg.name %> - v<%= pkg.version %> - ' +
    					'<%= grunt.template.today("yyyy-mm-dd") %> */',
				},
				files: {
					'static/assets/js/vendors.min.js': 'static/assets/js/vendors.js'
				}
			},
			development : {
				options: {
					beautify : true,
					mangle: true,
					compress: true,
					preserveComments: false,
					sourceMap: true,
					banner:  '/*! <%= pkg.name %> - v<%= pkg.version %> - ' +
    					'<%= grunt.template.today("yyyy-mm-dd") %> */',
				},
				files: {
					'static/assets/js/main.min.js': 'static/assets/js/main.js'
				}
			}
		},
		concat : {
			ngScripts : {
				src : [
					'static/modules/login/login.js',
					'static/modules/login/AuthService.js',
					'static/modules/home/home.js',
					'static/modules/forbidden/*.js',
					'static/modules/app.js',
					'static/modules/providers/*.js',
					'static/modules/constants/*.js',
					'static/modules/services/*.js',
					'static/modules/directives/*.js',
					'static/modules/order/orders.js',
					'static/modules/order/*.js',
					'static/modules/order/list/*.js',
					'static/modules/order/detail/*.js',
					'static/modules/deliveryguy/deliveryguy.js',
					'static/modules/deliveryguy/dgConstants.js',
					'static/modules/deliveryguy/dgFilter.js',
					'static/modules/deliveryguy/list/*.js',
					'static/modules/deliveryguy/create/*.js',
					'static/modules/deliveryguy/detail/*.js',
					'static/modules/vendor/vendor.js',
					'static/modules/vendor/list/*.js',
					'static/modules/reports/*.js',
					'static/modules/cod/cod.js',
					'static/modules/cod/deposit/*.js',
					'static/modules/cod/transfer/*.js',
					'static/modules/cod/history/*.js',
					'static/modules/feedback/feedback.js',
					'static/modules/feedback/list/*.js',
					'static/modules/feedback/detail/*.js',
					'static/modules/notification/notification.js',
					'static/modules/notification/noticeFromnowFilter.js',
				],
				dest : 'static/assets/js/main.js'
			}
		},
		watch : {
			scripts : {
				files : 'static/modules/**/*.js',
				tasks : ['devScripts']
			},
			sass : {
				files : 'static/assets/**/sass/**/*scss',
				tasks : ['compass:sass']
			}
		},
		compass : {
			sass : {
				options : {
					basePath:'static/assets',
					sassDir : "sass",
					cssDir : 'css',
					fontsDir: 'fonts',
					imagesDir :'images',
					outputStyle:'compressed',
					raw: 'preferred_syntax = :scss\n'
				}
			}
		}
	});
	require('load-grunt-tasks')(grunt);
	grunt.registerTask('buildbower', [
		'bower_concat',
		'uglify:bower'
	]);

	grunt.registerTask('bowerinstall', function(library) {
		grunt.task.run('shell:bowerinstall:' + library);
		grunt.task.run('buildbower');
	});

	grunt.registerTask('bowerupdate', function(library) {
		grunt.task.run('shell:bowerupdate:' + library);
		grunt.task.run('buildbower');
	});

	grunt.registerTask('devScripts',[
		'concat',
		'uglify:development'
	]);
};