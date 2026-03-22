#![no_std]

use soroban_sdk::{contract, contractimpl, symbol_short, token, Address, Env, String};

#[contract]
pub struct MiniRewardContract;

#[contractimpl]
impl MiniRewardContract {
    /// send_reward transfers a specified token amount from the teacher to the student,
    /// and emits a custom on-chain event with the teacher, student, and reason.
    pub fn send_reward(
        env: Env,
        token_address: Address,
        teacher: Address,
        student: Address,
        amount: i128,
        reason: String,
    ) {
        // Enforce the Teacher signed this invocation
        teacher.require_auth();

        // Execute the token transfer
        let token_client = token::Client::new(&env, &token_address);
        token_client.transfer(&teacher, &student, &amount);

        // Emit an event indicating a reward was distributed
        env.events()
            .publish((symbol_short!("reward"), teacher, student), reason);
    }
}

mod test;
