package com.emse.spring.automacorp.hello;

import org.springframework.stereotype.Service;

@Service
public class AnotherConsoleGreetingService implements  GreetingService{
    @Override
    public void greet(String name) {
        System.out.println("Bonjour, "+ name+ "!");
    }
}
