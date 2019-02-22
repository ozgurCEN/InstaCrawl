# InstaCrawl
A reliable Instagram crawler tool for non-private profiles


-----------------------------------

## Two classes, one for profile page and the other for post page

### class mainPage()

Methods:

#### basic_information(): 
This method returns profile owner's full name, count of followings, count of followers and count of post.

#### initial_post_list():
This method returns latest 24 posts and their date of releasing.

#### jump_to_post(post_num):
This method allows directs user to given post page and runs singlePost() class.
