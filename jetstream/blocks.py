from wagtail.wagtailcore import blocks
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailembeds.blocks import EmbedBlock

from .utils import SHOW_CHOICES, BACKGROUND_COLORS, FOREGROUND_COLORS, get_block_tuple, BlockTupleMixin

# =======
# Globals
# =======
wh_height_helptext = (
    'If "Fixed Dimensions" is checked, or if this block is placed outside a layout element (e.g. outside a N-Column "'
    'layout), set the image to be this many pixels tall.'
)

wh_width_helptext = (
    'If "Fixed Dimensions" is checked, or if this block is placed outside a layout element (e.g. outside a N-Column '
    'layout), set the image to be this many pixels wide.'
)

CYCLE_EFFECTS = [
    ('fade', 'Fade'),
    ('slide', 'Slide'),
]


# ====================
# Component Sub-blocks
# ====================
class LinkBlock(blocks.StructBlock):
    """
    Allows a user to optionally link the containing block to a Page or a relative or absolute URL.

    NOTE: Due to limitations in CSS, callers of LinkBlock() must not specify a label in the construction arguments.
    See the comment in the Meta class for why.

    NOTE: Within a template, checking for the existence of `self.link` will always return True because
    the existence of a class is always True even if the class has null contents. To check for a non-empty
    LinkBlock, use the `{% link_exists %}` template tag.
        ex. {% link_exists self.link as exists %}
            {% if exists %}
                `do something`
            {% endif %}
    """

    page = blocks.PageChooserBlock(
        required=False,
        help_text="Link to the chosen page. If both a page and a URL are specified, the page will take precedence."
    )
    url = blocks.CharBlock(
        required=False,
        help_text="Link to the given URL. This can be a relative URL to a location your own site (e.g. /example-page) "
                  "or an absolute URL to a page on another site (e.g. http://www.caltech.edu)."
    )

    def render_basic(self, value, context=None):
        """
        We can get away with not rendering the whole html <a> tag because we always reference the LinkBlock
        attribute of parent classes in the href attribute of an already specified <a> class.
        """
        if value['page']:
            return value['page'].full_url
        else:
            return value['url']

    class Meta:
        # By giving this entire block the label "Page", we can use some css in core/admin.less to "get rid of" the
        # unnecessary label that Wagtail adds to this block, by labeling the block as "Page" and then hiding the label
        # of the actual Page field. This is super gross, but there's no other way to do it because form_classname gets
        # applied to the preceding sibling of the offending label, rather than a parent.
        label = 'Page'
        form_classname = 'link-block'


class DimensionsOptionsBlock(blocks.StructBlock):
    """
    Allows the user to specify arbitrary dimensions for a block that has certain interactions with
    the various column layouts.
    """
    use = blocks.BooleanBlock(
        default=False,
        required=False,
        label='Use Fixed Dimensions',
        help_text="Normally, the image will expand its height to satisfy the suggested height on its parent block. "
                  "Checking this box will make it conform to the specified height and width, instead."
    )
    height = blocks.IntegerBlock(
        default=200,
        label="Height (pixels)",
        help_text=wh_height_helptext
    )
    width = blocks.IntegerBlock(
        default=200,
        label="Width (pixels)",
        help_text=wh_width_helptext
    )

    @property
    def media(self):
        return forms.Media(
            js=['core/js/admin/dimensions-options.js']
        )

    def js_initializer(self):
        return "fixed_dimensions"

    class Meta:
        form_classname = 'dimensions-options struct-block'


class ColorOptionsBlock(blocks.StructBlock):
    background_image = ImageChooserBlock(
        required=False,
        help_text="This image, if supplied, will appear as a background for this block"
    )
    background_color = blocks.ChoiceBlock(
        choices=BACKGROUND_COLORS,
        blank=False,
        required=False,
        default=BACKGROUND_COLORS[0],
        help_text="Set the background color of this block.  If a Background Image is also supplied, the Background "
                  "Image will be displayed instead of this color"
    )
    text_color = blocks.ChoiceBlock(
        choices=FOREGROUND_COLORS,
        blank=False,
        required=False,
        default=FOREGROUND_COLORS[0],
        help_text="Set the color for the text in this block. This is here so you can make your text visible on both "
                  "light and dark backgrounds."
    )

# ======================================================================================================
# ====================================== MEDIA BLOCKS ==================================================
# ======================================================================================================


class CaptionedImageBlock(blocks.StructBlock, BlockTupleMixin):
    image = ImageChooserBlock(required=True)
    fixed_dimensions = DimensionsOptionsBlock()

    class Meta:
        label = 'Captioned Image'
        template = 'core/blocks/captioned_image_block.html'
        form_classname = 'captioned-image struct-block'
        icon = 'image'


class ImageLinkBlock(blocks.StructBlock, BlockTupleMixin):

    image = ImageChooserBlock(required=True)
    title = blocks.CharBlock(required=False)
    subtitle = blocks.CharBlock(required=False)
    link = LinkBlock()
    fixed_dimensions = DimensionsOptionsBlock()

    class Meta:
        label = 'Image Link'
        template = 'core/blocks/image_link_block.html'
        form_classname = 'image-link struct-block'
        icon = 'image'


class ImagePanelBlock(blocks.StructBlock, BlockTupleMixin):
    STYLES = (
        ('rollover', 'Image Link w/ Rollover Text', 'core/blocks/image_panel_block-rollover.html', []),
        ('separate_text', 'Image Card (Equal Heights)', 'core/blocks/image_panel_block-image_card.html', ['equal']),
        ('separate_text_natural', 'Image Card (Natural Heights)', 'core/blocks/image_panel_block-image_card.html',
            ['natural']
         ),
        ('image_listing_left', 'Listing (Image Left)', 'core/blocks/image_panel_block-listing.html', ['left']),
        ('image_listing_right', 'Listing (Image Right)', 'core/blocks/image_panel_block-listing.html', ['right']),
        ('hero', 'Hero Image', 'core/blocks/image_panel_block-hero.html', []),
    )
    STYLE_TO_TEMPLATE_MAP = {style[0]: (style[2], style[3]) for style in STYLES}
    image_panel_wh_help_text = (
        "Width and Height are used based on which Style has been selected. Some styles ingore these settings unless "
        "Fixed Dimensions is checked. Others use them regardless."
    )

    image = ImageChooserBlock()
    style = blocks.ChoiceBlock(choices=[(style[0], style[1]) for style in STYLES], default=STYLES[0][0])
    title = blocks.CharBlock(required=False)
    desc = blocks.CharBlock(
        required=False,
        label="Body"
    )
    link = LinkBlock()
    fixed_dimensions = DimensionsOptionsBlock()

    class Meta:
        label = 'Image Panel'
        form_classname = 'image-panel struct-block'
        icon = 'image'

    def render(self, value, context=None):
        """
        We override this method to allow a template to be chosen dynamically based on the value of the "style" field.
        """
        try:
            (template, extra_classes) = self.STYLE_TO_TEMPLATE_MAP[value['style']]
        except KeyError:
            # If this block somehow doesn't have a known style, fall back to the basic_render() method.
            return self.render_basic(value, context=context)

        if context is None:
            new_context = self.get_context(value)
        else:
            new_context = self.get_context(value, parent_context=dict(context))
        new_context['extra_classes'] = " ".join(extra_classes)

        return mark_safe(render_to_string(template, new_context))


class HeroImageCarouselBlock(blocks.StructBlock, BlockTupleMixin):

    slides = blocks.ListBlock(
        blocks.StructBlock([
            ('image', ImageChooserBlock()),
            # 2016/07/19 - Commented out for now. I dont think an embedded video is what we actually want here, anyway.
            # ('video', EmbedBlock(
            #     required=False,
            #     help_text="If both a video and an image are selected, the video will take precedence."
            # )),
            ('title', blocks.CharBlock()),
            ('text', blocks.TextBlock()),
            ('link', LinkBlock()),
        ])
    )
    height = blocks.IntegerBlock(
        default=300,
        label="Hero Image Height (pixels)",
    )
    width = blocks.IntegerBlock(
        default=1000,
        label="Hero Image Width (pixels)",
    )
    cycle_effect = blocks.ChoiceBlock(choices=CYCLE_EFFECTS, default='slide')
    cycle_timeout = blocks.IntegerBlock(
        default=10000,
        help_text="The time between automatic image cycles (in milliseonds). Set to 0 to disable automatic cycling."
    )

    class Meta:
        template = 'core/blocks/hero_image_carousel_block.html'
        form_classname = 'image-carousel struct-block'
        label = 'Hero Image Slider'
        icon = 'image'


# TODO: This is a heck of a lot of overlap between HeroImageCarouselBlock and ImageCarouselBlock.
# Maybe write a parent class with their shared functionality?
class ImageCarouselBlock(blocks.StructBlock, BlockTupleMixin):

    header = blocks.TextBlock()
    slides = blocks.ListBlock(
        blocks.StructBlock([
            ('image', ImageChooserBlock()),
            ('text', blocks.CharBlock(required=False)),
            ('link', LinkBlock()),
        ])
    )
    cycle_timeout = blocks.IntegerBlock(
        default=5000,
        help_text="The time between automatic image cycles (in milliseonds). Set to 0 to disable automatic cycling."
    )

    class Meta:
        template = 'core/blocks/image_carousel_block.html'
        label = 'Image Carousel'
        icon = 'image'


# TODO: Convert the 'images' to a ListBlock.
class CaptionedImageCarouselBlock(blocks.StructBlock, BlockTupleMixin):
    images = blocks.StreamBlock([
        ('image', ImageChooserBlock()),
    ])

    class Meta:
        template = 'core/blocks/captioned_image_carousel_block.html'
        form_classname = 'captioned-slider struct-block'
        label = 'Captioned Image Slider'
        icon = 'image'


class SpacerBlock(blocks.StructBlock):

    height = blocks.ChoiceBlock(
        choices=[(x, x*25) for x in range(1, 10)],
        blank=False,
        default=1,
        label="Height (pixels)",
        help_text="Add empty vertical space whose height is this many pixels.")

    class Meta:
        label = 'Spacer'
        template = 'core/blocks/spacer_block.html'
        form_classname = 'spacer struct-block'
        icon = 'arrows-up-down'


class RelatedLinksNodeBlock(blocks.StructBlock):
    text = blocks.CharBlock(required=True)
    link = LinkBlock()


# TODO: Convert the 'links' to a ListBlock.
class RelatedLinksBlock(blocks.StructBlock, BlockTupleMixin):
    title = blocks.CharBlock(
        required=False,
        label='Title',
    )
    links = blocks.StreamBlock(
        [('link', RelatedLinksNodeBlock(label='Link'))],
        label='Links'
    )
    color = ColorOptionsBlock()
    fixed_dimensions = DimensionsOptionsBlock()

    class Meta:
        label = 'Related Links'
        template = 'core/blocks/related_links_block.html'
        form_classname = 'related-links struct-block'
        icon = 'list-ul'


class VideoBlock(blocks.StructBlock, BlockTupleMixin):

    video = EmbedBlock(
        label="Video Embed URL",
        help_text="Paste the video URL from YouTube or Vimeo. e.g. https://www.youtube.com/watch?v=l3Pz_xQZVDg "
                  "or https://vimeo.com/207076450."
    )
    title = blocks.CharBlock(required=False)

    fixed_dimensions = DimensionsOptionsBlock()

    class Meta:
        label = 'Video w/ Title'
        template = 'core/blocks/video_block.tpl'
        form_classname = 'video-block struct-block'
        icon = 'media'


STYLE_MAP = {'section_divider': 'core/blocks/heading-section_divider.html',
             'block_header': 'core/blocks/heading-block_header.html'}


class SectionTitleBlock(blocks.StructBlock, BlockTupleMixin):

    text = blocks.CharBlock(required=True)
    style = blocks.ChoiceBlock(
        choices=[
            ('section_divider', 'Section Divider'),
            ('block_header', 'Block Header'),
        ],
        requried=True,
        blank=False,
        default=('section_divider', 'Section Divider')
    )

    def render(self, value, context=None):
        if value['style']:
            setattr(self.meta, 'template', STYLE_MAP[value['style']])
        return super(SectionTitleBlock, self).render(value, context)

    class Meta:
        template = 'core/blocks/heading-section_divider.html'
        form_classname = 'section-title struct-block'
        label = 'Section Title'
        icon = 'form'


class MenuListingBlock(blocks.StructBlock, BlockTupleMixin):

    title = blocks.CharBlock(
        required=False,
        help_text="If supplied, display this at the top of the menu listing"
    )
    show = blocks.ChoiceBlock(
        choices=[
            ('siblings', 'Page Siblings'),
            ('children', 'Page Children')
        ],
        blank=False,
        default=('siblings', 'Page Siblings'),
        help_text='"Page Siblings" lists all pages at the same level of the site page heirarchy as this page; '
                  '"Page Children" lists all pages that are directly below this page in the page heirarchy.'
    )

    class Meta:
        template = 'core/blocks/menu_listing_block.html'
        form_classname = 'menu-listing struct-block'
        label = 'Menu Section'
        icon = 'list-ul'


class NewsListingBlock(blocks.StructBlock, BlockTupleMixin):

    title = blocks.CharBlock(
        required=False,
        help_text="If supplied, display this at the top of the news listing"
    )
    show = blocks.ChoiceBlock(
        choices=SHOW_CHOICES,
        blank=False,
        default=(5, 5),
        label="Number of News items to list"
    )
    color = ColorOptionsBlock()
    fixed_dimensions = DimensionsOptionsBlock()

    class Meta:
        template = 'core/blocks/news_listing_block.tpl'
        form_classname = 'news-listing struct-block'
        label = 'News Listing'
        icon = 'wagtail'


class FancyRichTextBlock(blocks.StructBlock, BlockTupleMixin):

    text = blocks.RichTextBlock(
        required=True,
        label="Body"
    )
    color = ColorOptionsBlock()
    fixed_dimensions = DimensionsOptionsBlock()

    class Meta:
        template = 'core/blocks/fancy_rich_text_block.html'
        form_classname = 'fancy-richtext struct-block'
        label = 'Rich Text'
        icon = 'doc-full'


# ==================
# Layout Blocks
# -----
# These go at the end because they need to include all of the previous content blocks.
# ==================
COLUMN_PERMITTED_BLOCKS = [
    get_block_tuple(FancyRichTextBlock()),
    get_block_tuple(ImageLinkBlock()),
    get_block_tuple(ImageCarouselBlock()),
    get_block_tuple(CaptionedImageBlock()),
    get_block_tuple(CaptionedImageCarouselBlock()),
    get_block_tuple(RelatedLinksBlock()),
    get_block_tuple(ImagePanelBlock()),
    get_block_tuple(VideoBlock()),
    get_block_tuple(SectionTitleBlock()),
    get_block_tuple(MenuListingBlock()),
    get_block_tuple(NewsListingBlock()),
    get_block_tuple(SpacerBlock()),
]

# Choices for col-md-## class used by bootstrap for grids
BS_COL_CHOICES = [(x, x) for x in range(1, 12)]
col_helptext = "Column width is represented as units out of twelve. EX. 6 / 12 units will take up half the container."
fixed_height_helptext = (
    "Blocks that contain images that are placed in one of the columns here will set themselves to this height unless "
    "specifically overridden on the block."
)


class BaseTwoColumnSubBlock(blocks.StructBlock, BlockTupleMixin):
    """
    Duplicate of BaseTwoColumnBlock without the sub block to avoid recursion.
    """
    left_column_width = blocks.ChoiceBlock(choices=BS_COL_CHOICES, blank=False, default=6, help_text=col_helptext)
    fixed_height = blocks.IntegerBlock(
        default=350,
        label="Suggested height for contained widgets",
        help_text="Blocks that contain images that are placed in one of the columns here will set themselves to this "
                  "height unless specifically overridden on the block."
    )
    gutter_width = blocks.ChoiceBlock(
        choices=[(12, 12), (20, 20), (30, 30), (40, 40)],
        blank=False,
        default=(12, 12),
        label="Column Gutter Width (pixels)",
        help_text="This determines how wide the spacing between columns will be, in pixels."
    )
    left_column = blocks.StreamBlock(COLUMN_PERMITTED_BLOCKS, icon='arrow-left', label='Left column content')
    right_column = blocks.StreamBlock(COLUMN_PERMITTED_BLOCKS, icon='arrow-right', label='Right column content')

    class Meta:
        template = 'core/blocks/two_column_block.html'
        form_classname = 'layout-two-column-sub struct-block'
        label = 'Two Columns'

    def get_block_tuple(self):
        """
        Overrides this method from BlockTupleMixin so that we use the same machine name as BaseTwoColumnBlock.
        """
        return ('two_column_layout', self)


class BaseTwoColumnBlock(blocks.StructBlock, BlockTupleMixin):
    """
    Base class to be overridden in implementing sub module with boilerplate implementation of column layout.
    """
    left_column_width = blocks.ChoiceBlock(choices=BS_COL_CHOICES, blank=False, default=6, help_text=col_helptext)
    fixed_height = blocks.IntegerBlock(
        default=350,
        label="Suggested height for contained widgets",
        help_text=fixed_height_helptext
    )
    gutter_width = blocks.ChoiceBlock(
        choices=[(12, 12), (20, 20), (30, 30), (40, 40)],
        blank=False,
        default=(12, 12),
        label="Column Gutter Width (pixels)",
        help_text="This determines how wide the spacing between columns will be, in pixels."
    )

    class Meta:
        template = 'core/blocks/two_column_block.html'
        form_classname = 'layout-two-column struct-block'
        label = 'Two Columns'

    def get_block_tuple(self):
        """
        Overrides this method from BlockTupleMixin so that we use the same machine name as BaseTwoColumnSubBlock.
        """
        return ('two_column_layout', self)


class BaseThreeColumnSubBlock(blocks.StructBlock, BlockTupleMixin):
    """
    Duplicate of BaseThreeColumnBlock without the sub block to avoid recursion.
    """
    left_column_width = blocks.ChoiceBlock(choices=BS_COL_CHOICES, blank=False, default=4, help_text=col_helptext)
    right_column_width = blocks.ChoiceBlock(choices=BS_COL_CHOICES, blank=False, default=4, help_text=col_helptext)
    fixed_height = blocks.IntegerBlock(
        default=300,
        label="Suggested height for contained widgets",
        help_text=fixed_height_helptext
    )
    gutter_width = blocks.ChoiceBlock(
        choices=[(12, 12), (20, 20), (30, 30), (40, 40)],
        blank=False,
        default=(12, 12),
        label="Column Gutter Width (pixels)",
        help_text="This determines how wide the spacing between columns will be, in pixels."
    )
    left_column = blocks.StreamBlock(COLUMN_PERMITTED_BLOCKS, icon='arrow-left', label='Left column content')
    middle_column = blocks.StreamBlock(COLUMN_PERMITTED_BLOCKS, icon='arrow-right', label='Middle column content')
    right_column = blocks.StreamBlock(COLUMN_PERMITTED_BLOCKS, icon='arrow-right', label='Right column content')

    class Meta:
        template = 'core/blocks/three_column_block.html'
        form_classname = 'layout-three-column-sub struct-block'
        label = 'Three Columns'

    def get_block_tuple(self):
        """
        Overrides this method from BlockTupleMixin so that we use the same machine name as BaseThreeColumnSubBlock.
        """
        return ('three_column_layout', self)


class BaseThreeColumnBlock(blocks.StructBlock, BlockTupleMixin):

    left_column_width = blocks.ChoiceBlock(choices=BS_COL_CHOICES, blank=False, default=4, help_text=col_helptext)
    right_column_width = blocks.ChoiceBlock(choices=BS_COL_CHOICES, blank=False, default=4, help_text=col_helptext)
    fixed_height = blocks.IntegerBlock(
        default=300,
        label="Suggested height for contained widgets",
        help_text=fixed_height_helptext
    )
    gutter_width = blocks.ChoiceBlock(
        choices=[(12, 12), (20, 20), (30, 30), (40, 40)],
        blank=False,
        default=(12, 12),
        label="Column Gutter Width (pixels)",
        help_text="This determines how wide the spacing between columns will be, in pixels."
    )

    class Meta:
        template = 'core/blocks/three_column_block.html'
        form_classname = 'layout-three-column struct-block'
        label = 'Three Columns'

    def get_block_tuple(self):
        """
        Overrides this method from BlockTupleMixin so that we use the same machine name as ThreeColumnSubBlock.
        """
        return ('three_column_layout', self)


class BaseFourColumnBlock(blocks.StructBlock, BlockTupleMixin):

    column_one_width = blocks.ChoiceBlock(choices=BS_COL_CHOICES, blank=False, default=3, help_text=col_helptext)
    column_two_width = blocks.ChoiceBlock(choices=BS_COL_CHOICES, blank=False, default=3, help_text=col_helptext)
    column_three_width = blocks.ChoiceBlock(choices=BS_COL_CHOICES, blank=False, default=3, help_text=col_helptext)
    fixed_height = blocks.IntegerBlock(
        default=250,
        label="Suggested height for contained widgets",
        help_text=fixed_height_helptext
    )
    gutter_width = blocks.ChoiceBlock(
        choices=[(12, 12), (20, 20), (30, 30), (40, 40)],
        blank=False,
        default=(12, 12),
        label="Column Gutter Width (pixels)",
        help_text="This determines how wide the spacing between columns will be, in pixels."
    )

    class Meta:
        template = 'core/blocks/four_column_block.html'
        form_classname = 'layout-four-column struct-block'
        label = 'Four Columns'

    def get_block_tuple(self):
        """
        Overrides this method from BlockTupleMixin so that we use the legacy machine name.
        """
        return ('four_column_layout', self)


class BaseSidebarLayoutBlock(blocks.StructBlock, BlockTupleMixin):

    sidebar_width = blocks.ChoiceBlock(choices=BS_COL_CHOICES, blank=False, default=4, help_text=col_helptext)
    sidebar_alignment = blocks.ChoiceBlock(choices=[
        ('left', 'Left'),
        ('right', 'Right'),
        ], blank=False, default='left')

    fixed_height = blocks.IntegerBlock(
        default=250,
        label="Suggested height for contained widgets",
        help_text=fixed_height_helptext
    )

    class Meta:
        template = 'core/blocks/sidebar_layout_block.html'
        form_classname = 'layout-sidebar struct-block'
        label = 'Sidebar Layout'