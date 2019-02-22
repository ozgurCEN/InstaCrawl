# InstaCrawl
A reliable Instagram crawler tool for non-private profiles


-----------------------------------



Two classes, one for profile page and the other for post page

### class mainPage()

#### Methods:

##### basic_information(): 
This method returns profile owner's full name, account privacy, count of followings, count of followers and count of post.

##### initial_post_list():
This method returns latest 24 posts and their date of publishing if the profile is not private.

##### jump_to_post(post_num):
This method directs user to given post page and runs singlePost() class if the profile is not private.

###

### class sinlePost()

#### Methods:

##### likes_and_views():
This method returns "like" count if the post is a photo else, it returns "like" and "view" counts of the video.

##### publish_time():
This method returns date of publishing of the post.

##### post_descr():
This method returns the information about the post that profile owner entered.

##### number_of_comments():
This method returns the count of comments written to the post.

##### last_n_comments_to_DF():
This method loads last n comments into a pandas.DataFrame with comments' owners.

##### download_post():
This method downloads the post (either photo or video) to working directory. 
