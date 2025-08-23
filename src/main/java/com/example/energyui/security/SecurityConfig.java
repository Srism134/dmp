package com.example.energyui.security;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;
import org.springframework.security.web.SecurityFilterChain;

import static org.springframework.security.config.Customizer.withDefaults;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

  @Bean
  public InMemoryUserDetailsManager users() {
    UserDetails admin = User.withUsername("admin").password("{noop}admin").roles("ADMIN").build();
    UserDetails user  = User.withUsername("user").password("{noop}user").roles("USER").build();
    return new InMemoryUserDetailsManager(admin, user);
  }

  @Bean
  public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http.csrf(csrf -> csrf.disable())
      .authorizeHttpRequests(auth -> auth
        .requestMatchers("/error","/mock/**","/css/**","/js/**","/images/**").permitAll()
        .anyRequest().authenticated())
      .formLogin(withDefaults())     // <-- use Spring's default /login page
      .logout(logout -> logout.logoutSuccessUrl("/login?logout").permitAll());
    return http.build();
  }
}