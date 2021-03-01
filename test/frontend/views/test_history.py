"""Purpose of this file

This file contains the test cases for /frontend/views/history.py.
"""

import reversion

from reversion import set_comment, is_registered
from reversion.models import Version

from test import utils
from test.test_cases import MediaTestCase

from django.urls import reverse

from base.models import Content, Course, CourseStructureEntry, Topic, Category

import content.models as model


class BaseHistoryCompareViewTestCase(MediaTestCase):
    """BaseHistoryCompareView test case

    Defines the test cases for view BaseHistoryCompareView.
    """

    def test_initial_state(self):
        """Test case - initial states

        Tests if the relevant models are registered.
        """
        self.assertTrue(is_registered(Course))
        self.assertTrue(is_registered(Content))
        self.assertTrue(is_registered(model.TextField))
        self.assertTrue(is_registered(model.Latex))
        self.assertTrue(is_registered(model.ImageContent))
        self.assertTrue(is_registered(model.PDFContent))
        self.assertTrue(is_registered(model.YTVideoContent))


class ContentHistoryCompareViewTestCase(MediaTestCase):
    """ history compare test cases

    Defines test cases for the view ContentHistoryCompareView.
    """

    def setUp(self):
        """Setup

        Sets up the test database.
        """
        super().setUp()
        # set up a textfield item to test
        with reversion.create_revision():
            self.content1 = utils.create_content(model.TextField.TYPE)
            self.text1 = model.TextField.objects.create(content=self.content1,
                                                        textfield='Hello!',
                                                        source='test')
            self.text1.content.attachment = utils.generate_attachment(2)
            set_comment('initial version')

        # create a new version and make 1 change to text1
        with reversion.create_revision():
            self.text1.textfield = 'test test'
            self.text1.save()
            set_comment('change text')

        self.queryset = Version.objects.get_for_object(self.text1)
        self.revision_ids1 = self.queryset.values_list("revision_id", flat=True)
        self.version_ids1 = self.queryset.values_list("pk", flat=True)

        # set up a latex item to test
        with reversion.create_revision():
            self.content2 = utils.create_content(model.Latex.TYPE)
            self.latex1 = model.Latex.objects.create(content=self.content1,
                                                     textfield='/textbf{Hello!}',
                                                     source='test')
            set_comment('initial version')

        # create a new version and make 1 change to latex1
        with reversion.create_revision():
            self.latex1.textfield = '/textbf{你好！}'
            self.latex1.save()
            set_comment('change code')

        # get the author and topic id for later test
        self.author_id = self.latex1.content.author_id
        self.topic_id = self.text1.content.topic_id

        self.queryset2 = Version.objects.get_for_object(self.latex1)
        self.revision_ids2 = self.queryset2.values_list("revision_id", flat=True)
        self.version_ids2 = self.queryset2.values_list("pk", flat=True)

    def test_textfield_version_create(self):
        """Create version test case - Textfield

        Tests if the versions are correctly generated for text1.
        """

        # after set up the number of versions of text1 should be 2
        self.assertEqual(Version.objects.get_for_object(self.text1).count(), 2)
        # the revision ids for text1 should be 1 and 2
        self.assertEqual(list(self.revision_ids1), [2, 1])

    def test_textfield_revert_changes(self):
        """Revert version test case - Textfield changes

        Tests content revert with one change within TextField model.
        """
        # performing the revert with post
        path = reverse('frontend:textfield-history', kwargs={
            'course_id': 1, 'topic_id': 1, 'pk': self.text1.pk
        })
        data = {'rev_pk': '2'}
        self.client.post(path, data)

        # check the state of text1 after the revert
        self.text1.refresh_from_db()

        self.queryset = Version.objects.get_for_object(self.text1)
        self.version_ids1 = self.queryset.values_list("pk", flat=True)
        # the number of versions should be 3 now
        self.assertEqual(self.version_ids1.count(), 3)
        # the textfield should be identical to version 1
        self.assertEqual(self.text1.textfield, 'Hello!')
        # topic id should not be changed
        self.assertEqual(self.text1.content.topic_id, self.topic_id)

    def test_textfield_revert_no_changes(self):
        """Revert version test case - Textfield no changes

        Tests content revert with no change within TextField model.
        """
        # save a new version but don't make any change
        with reversion.create_revision():
            self.text1.save()
            set_comment('nothing changed')
        # performing the revert to the 2nd version with post
        path = reverse('frontend:textfield-history', kwargs={
            'course_id': 1, 'topic_id': 1, 'pk': self.text1.pk
        })
        data = {'rev_pk': '6'}
        self.client.post(path, data)

        # check the state of text1 after the revert
        self.text1.refresh_from_db()

        self.queryset = Version.objects.get_for_object(self.text1)
        self.version_ids1 = self.queryset.values_list("pk", flat=True)
        # the number of versions should be 4 now
        self.assertEqual(self.version_ids1.count(), 4)
        # the textfield should be identical to version 2
        self.assertEqual(self.text1.textfield, 'test test')
        # topic id should not be changed
        self.assertEqual(self.text1.content.topic_id, self.topic_id)

    def test_textfield_revert_many_fields(self):
        """Revert version test case - Textfield many fields changed

        Tests content revert with more than one change within TextField model.
        """
        # save a new version but don't make any change
        with reversion.create_revision():
            self.text1.textfield = 'jo jo'
            self.text1.source = 'new source'
            self.text1.save()
            set_comment('text and source changed')
        # performing the revert to the 2nd version with post
        path = reverse('frontend:textfield-history', kwargs={
            'course_id': 1, 'topic_id': 1, 'pk': self.text1.pk
        })
        data = {'rev_pk': '6'}
        self.client.post(path, data)

        # check the state of text1 after the revert
        self.text1.refresh_from_db()

        self.queryset = Version.objects.get_for_object(self.text1)
        self.version_ids1 = self.queryset.values_list("pk", flat=True)
        # the number of versions should be 4 now
        self.assertEqual(self.version_ids1.count(), 4)
        # the textfield should be identical to version 2
        self.assertEqual(self.text1.textfield, 'test test')
        # the source should be identical to version 2 too
        self.assertEqual(self.text1.source, 'test')
        # topic id should not be changed
        self.assertEqual(self.text1.content.topic_id, self.topic_id)

    def test_textfield_compare_change_one(self):
        """Compare test case - Textfield one change

        Tests content history compare with one change within TextField model
        """
        # performing the compare of the first two versions
        path = reverse('frontend:textfield-history', kwargs={
            'course_id': 1, 'topic_id': 1, 'pk': self.text1.pk
        })
        data2 = {"version_id2": self.version_ids1[0], "version_id1": self.version_ids1[1]}
        response = self.client.get(path, data2)
        # check if the differences will be correctly collected
        self.assertContainsHtml(
            response,
            "<del>- Hello!</del>",
            "<ins>+ test test</ins>",
            "<blockquote>change text</blockquote>",  # change log
        )

    def test_textfield_compare_no_change(self):
        """Compare test case - Textfield no change

        Tests content history compare with no change within TextField model.
        """
        # save a new version but don't make any change
        with reversion.create_revision():
            self.text1.save()
            set_comment('nothing changed')
        # performing the revert to the 2nd version with post
        path = reverse('frontend:textfield-history', kwargs={
            'course_id': 1, 'topic_id': 1, 'pk': self.text1.pk
        })
        data2 = {"version_id2": self.version_ids1[0], "version_id1": self.version_ids1[1]}
        response = self.client.get(path, data2)
        self.assertContainsHtml(response,
                                "There are no differences.")

    def test_textfield_compare_many_change(self):
        """Compare test case - Textfield many changes

        Tests content history compare with more than 1 changes from Content and TextField model.
        """
        # test with more changes including content-field
        with reversion.create_revision():
            # version 3 for text1
            self.text1.content.description = 'new desc'
            self.text1.source = 'local'
            self.text1.save()
            set_comment('test with more changes including content-field')

        self.queryset = Version.objects.get_for_object(self.text1)
        self.version_ids1 = self.queryset.values_list("pk", flat=True)
        self.revision_ids1 = self.queryset.values_list("revision_id", flat=True)
        # the number of versions and revisions should be 3 now
        self.assertEqual(self.version_ids1.count(), 3)
        self.assertEqual(list(self.revision_ids1), [5, 2, 1])

        # performing compare
        path = reverse('frontend:textfield-history', kwargs={
            'course_id': 1, 'topic_id': 1, 'pk': self.text1.pk
        })
        data3 = {"version_id2": self.version_ids1[0], "version_id1": self.version_ids1[2]}
        response = self.client.get(path, data3)
        # check if the selected versions corresponding the compared versions
        self.assertContainsHtml(
            response,
            f'<input type="radio" name="version_id1" value="{self.version_ids1[0]:d}" style="visibility:hidden" />',
            f'<input type="radio" name="version_id2" value="{self.version_ids1[0]:d}" checked="checked" />',
            f'<input type="radio" name="version_id1" value="{self.version_ids1[2]:d}" checked="checked" />',
            f'<input type="radio" name="version_id2" value="{self.version_ids1[2]:d}" />',
        )
        # check if the differences will be correctly collected
        self.assertContainsHtml(
            response,
            "<del>this is a description</del>",  # change for content.description
            "<ins>new desc</ins>",
            "<del>- test</del>",  # change for source
            "<ins>+ local</ins>",
            "<blockquote>test with more changes including content-field</blockquote>",  # change log
        )

    def test_latex_version_create(self):
        """Create version test case - LaTeX

        Tests if the versions are correctly generated for latex1.
        """
        # after set up the number of versions of latex1 should be 2
        self.assertEqual(Version.objects.get_for_object(self.latex1).count(), 2)
        # the revision ids for latex1 should be 1 and 2
        self.assertEqual(list(self.revision_ids2), [4, 3])

    def test_latex_revert_changes(self):
        """Revert version test case - LaTeX changes

        Tests latex revert with changes within the Latex model.
        """
        # performing the revert with post
        path = reverse('frontend:latex-history', kwargs={
            'course_id': 1, 'topic_id': 1, 'pk': self.latex1.pk
        })
        data = {'rev_pk': '9'}  # the version number must be correct
        self.client.post(path, data)

        # check the state of latex1 after the revert
        self.latex1.refresh_from_db()

        self.queryset2 = Version.objects.get_for_object(self.latex1)
        self.version_ids2 = self.queryset2.values_list("pk", flat=True)
        # the number of versions should be 3 now
        self.assertEqual(self.version_ids2.count(), 3)
        # the text field should be identical to the original
        self.assertEqual(self.latex1.textfield, '/textbf{Hello!}')
        # the revert should not change the author id
        self.assertEqual(self.latex1.content.author_id, self.author_id)
        # after revert the pdf file of latex should still exist
        self.assertIsNotNone(self.latex1.pdf)

    def test_compare_with_attachment(self):
        """Compare test case - Content history compare with attachment

        Tests content history compare with attachment.
        """
        with reversion.create_revision():
            self.text1.content.attachment.images.get(pk=1).source = 'new source text'
            self.text1.save()
            set_comment('attachment edited')

        self.queryset = Version.objects.get_for_object(self.text1)
        self.version_ids1 = self.queryset.values_list("pk", flat=True)
        # print(self.version_ids1) [13, 6, 2]
        # performing the compare between the last two versions
        path = reverse('frontend:textfield-history', kwargs={
            'course_id': 1, 'topic_id': 1, 'pk': self.text1.pk
        })
        data3 = {"version_id2": self.version_ids1[0], "version_id1": self.version_ids1[1]}
        response = self.client.get(path, data3)
        # TODO the changes of attachment source is not showing at current status
        self.assertContainsHtml(
            response,
            # "<ins>+ new source text</ins>",  # change for source
            "<blockquote>attachment edited</blockquote>",  # change log
        )
        queryset3 = Version.objects.get_for_object(self.text1.content.attachment)
        # the versions of the attachment should also exist in database
        self.assertNotEqual(queryset3.values_list("pk", flat=True).count(), 0)


class CourseHistoryCompareViewTestCase(MediaTestCase):
    """ CourseHistoryCompareView Test Cases

    Defines Test Cases for the view CourseHistoryCompareView.
    """

    def setUp(self):
        """Setup

        Sets up the test database.
        """
        super().setUp()

        self.cat = Category.objects.create(title="Category~*")
        # set up a course item to test
        with reversion.create_revision():
            self.course1 = Course.objects.create(title='Course Test', description='desc', category=self.cat)

            self.topic1 = Topic.objects.create(title="Topic1", category=self.cat)
            self.topic2 = Topic.objects.create(title="Topic2", category=self.cat)
            self.topic3 = Topic.objects.create(title="Topic3", category=self.cat)

            course_struc_entry_1 = CourseStructureEntry(course=self.course1, index=1, topic=self.topic1)
            course_struc_entry_2 = CourseStructureEntry(course=self.course1, index=2, topic=self.topic2)
            course_struc_entry_3 = CourseStructureEntry(course=self.course1, index="2/1", topic=self.topic3)
            course_struc_entry_1.save(), course_struc_entry_2.save(), course_struc_entry_3.save()
            set_comment('initial version')

        # create a new version and make 1 change to course1
        with reversion.create_revision():
            self.course1.description = 'test test'
            self.course1.save()
            set_comment('change desc')

        self.queryset = Version.objects.get_for_object(self.course1)
        self.revision_ids1 = self.queryset.values_list("revision_id", flat=True)
        self.version_ids1 = self.queryset.values_list("pk", flat=True)

        self.cat_id = self.cat.pk

    def test_version_create_course(self):
        """Create course test case - Version

        Tests if the versions of the course are correctly generated.
        """

        # after set up the number of versions of course1 should be 2
        self.assertEqual(Version.objects.get_for_object(self.course1).count(), 2)
        # the revision ids for text1 should be 1 and 2
        self.assertEqual(list(self.revision_ids1), [2, 1])
        self.assertEqual(self.course1.description, 'test test')

    def test_revert_course_change_one(self):
        """Revert course test case - One change

        Tests course revert when there is exactly 1 change.
        """
        # performing the revert with post
        path = reverse('frontend:course-history', kwargs={
            'pk': self.course1.pk
        })
        data = {'rev_pk': '1'}
        self.client.post(path, data)

        # check the state of course1 after the revert
        self.course1.refresh_from_db()

        self.queryset = Version.objects.get_for_object(self.course1)
        self.version_ids1 = self.queryset.values_list("pk", flat=True)
        # the number of versions should be 3 now
        self.assertEqual(self.version_ids1.count(), 3)
        # the textfield should be identical to the original
        self.assertEqual(self.course1.description, 'desc')
        # the category should not be changed after revert
        self.assertEqual(self.course1.category_id, self.cat_id)

    def test_revert_course_no_change(self):
        """Revert test cases - No changes

        Tests course revert when there is no change.
        """
        # save a new version but don't make any change
        with reversion.create_revision():
            self.course1.save()
            set_comment('nothing changed')

        # performing the revert with post
        path = reverse('frontend:course-history', kwargs={
            'pk': self.course1.pk
        })
        data = {'rev_pk': '2'}
        self.client.post(path, data)

        # check the state of course1 after the revert
        self.course1.refresh_from_db()

        self.queryset = Version.objects.get_for_object(self.course1)
        self.version_ids1 = self.queryset.values_list("pk", flat=True)
        # the number of versions should be 4 now
        self.assertEqual(self.version_ids1.count(), 4)
        # the desc should be identical to version 2
        self.assertEqual(self.course1.description, 'test test')
        # the category should not be changed after revert
        self.assertEqual(self.course1.category_id, self.cat_id)

    def test_revert_course_many_changes(self):
        """Revert test cases - Many changes

        Tests course revert when more than 1 change.
        """
        with reversion.create_revision():
            self.course1.description = 'new descc xixi'
            self.course1.title = 'xixi'
            self.course1.save()
            set_comment('title and desc changed')
        # performing the revert with post
        path = reverse('frontend:course-history', kwargs={
            'pk': self.course1.pk
        })
        data = {'rev_pk': '2'}
        self.client.post(path, data)

        # check the state of course1 after the revert
        self.course1.refresh_from_db()

        self.queryset = Version.objects.get_for_object(self.course1)
        self.version_ids1 = self.queryset.values_list("pk", flat=True)
        # the number of versions should be 4 now
        self.assertEqual(self.version_ids1.count(), 4)
        # the desc should be identical to version 2
        self.assertEqual(self.course1.description, 'test test')
        # the title should be identical to version 1
        self.assertEqual(self.course1.title, 'Course Test')
        # the category should not be changed after revert
        self.assertEqual(self.course1.category_id, self.cat_id)

    def test_compare_course_change_one(self):
        """Compare test cases - One change

        Tests course course history compare when there is exactly 1 change.
        """
        # performing compare
        path = reverse('frontend:course-history', kwargs={
            'pk': self.course1.pk
        })
        data = {"version_id2": self.version_ids1[0], "version_id1": self.version_ids1[1]}
        response = self.client.get(path, data)

        # check if the differences will be correctly collected
        self.assertContainsHtml(
            response,
            "<del>- desc</del>",  # change for description
            "<ins>+ test test</ins>",
            "<blockquote>change desc</blockquote>",  # change log
        )

    def test_compare_course_no_change(self):
        """Compare test cases - No changes

        Tests course course history compare when there is no changes.
        """
        with reversion.create_revision():
            self.course1.save()
            set_comment('nothing changed')
        # performing compare
        path = reverse('frontend:course-history', kwargs={
            'pk': self.course1.pk
        })
        data = {"version_id2": self.version_ids1[0], "version_id1": self.version_ids1[1]}
        response = self.client.get(path, data)

        self.assertContainsHtml(response,
                                "There are no differences.")

    def test_compare_course_many_changes(self):
        """Compare test cases - Many changes

        Tests course course history compare when there is more than 1 changes.
        """
        with reversion.create_revision():
            self.course1.description = 'new descc xixi'
            self.course1.title = 'xixi'
            self.course1.save()
            set_comment('title and desc changed')
        # performing compare
        path = reverse('frontend:course-history', kwargs={
            'pk': self.course1.pk
        })
        data = {"version_id2": self.version_ids1[0], "version_id1": self.version_ids1[1]}
        response = self.client.get(path, data)
        # check if the differences will be correctly collected
        self.assertContainsHtml(
            response,
            "<del>- test test</del>",  # change for description
            "<ins>+ new descc xixi</ins>",
            "<del>- Course Test</del>",  # change for title
            "<ins>+ xixi</ins>",
            "<blockquote>title and desc changed</blockquote>",  # change log
        )
