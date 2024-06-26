# Moderation api

welcome to moderation api, this api is designed for slow processing of
images and potentially long text heavy-duty stuff,
that's why it leverages fastapi's background tasks alongside Redis
each endpoint will immediately return an uuid (uuid v4 to be exact).

## how to run :

### locally with GitHub

Start a new terminal session and clone the project with this command :

```shell
git clone github.com/brahimabd98/moderation_api_py/
```

cd into the project :

```shell
cd moderation_api_py
```

Start a new venv (optional):

```shell
python -m venv .venv
```

Install the project's dependencies:

```shell
pip install -r requirements requirements.txt
```

**set up the .env file (checkout .env.example)**

start the project

```shell
fastapi run main.py --port 8000
```

### Redis:

- **make sure you have a running Redis db instance, you can check their docs for more [info](https://redis.com)**

## docker:

You can use the provided docker
images [here](https://github.com/brahimABD98/moderation_api_py/pkgs/container/moderation_api_py)

# disclaimers :

- ethical considerations:
  as the author of the different AI models, these kinds of classifications
  shouldn't be taken at face value and human intervention should
  present for the final decision.
- performance: this API uses very heavy AI pretrained models they are not
  meant for serverless environment, and it was made for to run in dedicated server
  so execution time isn't a consideration at all and as always
  measure because, depending on your use-case, it can perform very well even
  within lambda constraints.
  ## important
    - Error handling: right now there's no any kind of error handling whatsoever, so the server is prone to **crashing**
    - failed task: **Failed tasks will get stuck in pending status** there's no re-execution mechanism present yet,
      future releases might address that.
    - logging: there's no logging present at the moment so bring your own monitoring solutions

## features:

* Image moderation:
    * nsfw score: ranging from 0 to approx 1
    * normal score : ranging from 0 to approx 1
    * summary: to be improved, right now it just describes whether the image is nsfw with a thresh-hold of 0.5
      for better readability.
* Text moderation:
    * toxicity
    * severe toxicity
    * obscene
    * identity attack: current identities are
        * male
        * female
        * LGBT
        * christian
        * jewish
        * muslim
        * black
        * white
        * psychiatric_or_mental_illness
    * insult
    * threat
    * sexual explicit content
    * summary: to be improved upon, right now it just describes the current issues with the text based on score
      thresh-hold of 0.5 for better readability
* background tasks:
  All the moderation tasks are performed as a background task and saved inside a Redis database.

## Planned Improvements:

Other than using better models, of course, there are a couple of features to be considered a nice to have per se

- rate limiting: limit the amount of request, so it doesn't get overwhelmed
- failed tasks:
    - a queue for tasks similar to kafka.
    - Tasks that have failed won't be lost or stuck.
- better logging:
    - tracing: provide better logging for each task performed
- caching: Add caching for get_task endpoint
- Bulk image moderation: Like mentioned before, this is made for heavy-duty execution, so it should be able to pass s3
  bucket and
  be able to mass process all content within that bucket.
- Bulk text moderation: Maybe it could connect to a db and get certain posts or things like that.
  I couldn't think of a solution not tightly coupled with my project. I will make it, but I doubt it will make the
  public version

## Non-goals (subject to change) :

- Stuff like multiple images processing: I mean instead of image you get a list of images.
- html sanitization: this is just a frontend for classification models.
- censorship: apply blur filter or text censorship of certain words, it could be interesting but there are more
  important features should be implemented first
- measuring model performance: Despite being somewhat important, this won't be a goal, but it could be an interesting
  topic for sure

#### Notes:

* nsfw: not safe for work
* AI : artificial intelligence
* models : artificial intelligence models

credit: Brahim Abderrahim, 2024 