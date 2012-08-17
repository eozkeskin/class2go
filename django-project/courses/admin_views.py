from django.http import HttpResponsefrom django.shortcuts import render_to_response, redirectfrom django.template import Context, loaderfrom django.template import RequestContextfrom django.contrib.auth.models import User,Groupfrom courses.common_page_data import get_common_page_datafrom c2g.models import Course, Institution, AdditionalPagefrom random import randrangeimport datetimedef admin(request, course_prefix, course_suffix):    print "pref: " +str(course_prefix)    print "suff: " +str(course_suffix)    try:        common_page_data = get_common_page_data(request, course_prefix, course_suffix)    except:        raise Http404    return render_to_response('courses/admin.html', {'common_page_data':common_page_data}, context_instance=RequestContext(request))def new(request):    if request.method == 'POST':        #inst_id = request.POST.get('institution')        # We are disabling the institutions functionality temporarily        handle = request.POST.get('prefix') + '#$!' + request.POST.get('suffix')        ### Sanity checks ###        # Verify that the user is marked as staff member and, thus, has privilege to create a course        if not request.user.is_staff:            return HttpResponse('You are not allowed to create courses on Class2Go. If you feel this is an error, please contact the Class2Go team.')        # Verify that there is no course with the same handle        num_courses_with_same_handle = Course.objects.filter(handle=handle).count()        if num_courses_with_same_handle > 0:            return HttpResponse('A course with the same prefix and suffix already exists. Please choose a different prefix and/or suffix.')        ### Create the new Course ###        r = randrange(0,100000000)        student_group = Group.objects.create(name="Student Group for class2go course " + handle + " %d" % r)        instructor_group = Group.objects.create(name="Instructor Group for class2go course " + handle + " %d" % r)        tas_group = Group.objects.create(name="TAS Group for class2go course " + handle + " %d" % r)        readonly_tas_group = Group.objects.create(name="Readonly TAS Group for class2go course " + handle + " %d" % r)        #Add the professor to the instructor group        instructor_group.user_set.add(request.user)        start_date_elements = request.POST.get('start_date').split('-')        start_date_month = int(start_date_elements[0])        start_date_day = int(start_date_elements[1])        start_date_year = int(start_date_elements[2])        end_date_elements = request.POST.get('end_date').split('-')        end_date_month = int(end_date_elements[0])        end_date_day = int(end_date_elements[1])        end_date_year = int(end_date_elements[2])        # Create the course        staging_course = Course(            student_group_id = student_group.id,            instructor_group_id = instructor_group.id,            tas_group_id = tas_group.id,            readonly_tas_group_id = readonly_tas_group.id,            title = request.POST.get('title'),            term = request.POST.get('term'),            year = int(request.POST.get('year')),            calendar_start = datetime.datetime(start_date_year, start_date_month, start_date_day),            calendar_end = datetime.datetime(end_date_year, end_date_month, end_date_day),            list_publicly = 0,            mode='staging',            handle=handle,        )        staging_course.save()                staging_course.create_production_instance()                op = AdditionalPage(            course=staging_course,            menu_slug='course_info',            title='Overview',            description='',            slug='overview',            index=0,            mode='staging',        )        op.save()        op.create_production_instance()            request.session['course_mode'] = 'staging'        return redirect('courses.views.main', course_prefix = request.POST.get('prefix'), course_suffix = request.POST.get('suffix'))            else:        now = datetime.datetime.now()        date = "%02d-%02d-%04d" %(now.month, now.day, now.year)                # List of institutions        institutions = Institution.objects.all()                return render_to_response('courses/new.html', {'request': request, 'date': date, 'institutions': institutions }, context_instance=RequestContext(request))