[![Build Status](https://travis-ci.com/JmlrOrg/webpage.svg?branch=main)](https://travis-ci.com/JmlrOrg/webpage)

# Webpage
Sources for the [JMLR webpage](http://jmlr.org)

# To build and view the website locally

  1. Clone this repo with all its submodules:
      ```
      $ git clone --recurse-submodules -j8 https://github.com/JmlrOrg/webpage.git jmlr_webpage
      ```

  2. Build the webpage. The following command assumes that you have NodeJS and Python installed:
 
      ```
      $ make
      ```

  3. Run a local server
 
      ```
      $ make develop
      ```


# Some useful commands


* Update all submodules to latest commit:

    ```
    $ make update
    ```

