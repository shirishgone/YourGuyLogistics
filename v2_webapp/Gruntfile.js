module.exports = function(grunt){
	grunt.initConfig({
		pkg: grunt.file.readJSON('package.json'),
		bower_concat: {
			all: {
				dest: 'static/assets/js/vendors.js',
				exclude: [
					'angular-material-sass-files'
				]
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
					return 'bower update ' + libname;
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
};