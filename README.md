[![CircleCI](https://circleci.com/gh/JmlrOrg/webpage.svg?style=svg)](https://circleci.com/gh/JmlrOrg/webpage)

# Webpage
Sources for the [JMLR webpage](http://jmlr.org). 

## Reporting errors
If you found a typo or error, or have a feature request for the jmlr.org webpage, please submit an issue [here](https://github.com/JmlrOrg/webpage/issues) or send a pull request against this repository (or any of its submodules).

Note however that **this repository is relative to the public jmlr.org webpage, not the submission system**. For issues regarding the submission system, please follow the instructions in https://jmlr.org/contact.html

# To build and view the website locally

  1. Clone this repo with all its submodules:
      ```
      git clone --recurse-submodules -j8 https://github.com/JmlrOrg/webpage.git jmlr_webpage
      ```

  2. Build the webpage. The following command assumes that you have NodeJS and Python installed:
 
      ```
      make
      ```

  3. Run a local server
 
      ```
      make develop
      ```


# Some useful commands


* Update all submodules to latest commit:

    ```
    make update
    ```

