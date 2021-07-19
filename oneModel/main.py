import interpreter 

while True:
    text = input('basic > ')
    if text.strip() == "": continue

    result, error = interpreter.run('<stdin>', text)
    
    if error:
        print(error.as_string())
    elif result:
        # TODO: recover the result.elements
        print(repr(result))
        #if len(result.elements) == 1:
        #    print(repr(result.elements[0]))
        #else:
        #    print(repr(result))